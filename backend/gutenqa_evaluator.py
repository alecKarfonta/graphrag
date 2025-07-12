#!/usr/bin/env python3
"""
GutenQA Retrieval Evaluation System

Evaluates retrieval performance using the GutenQA dataset from LumberChunker.
This dataset contains 100 books from Project Gutenberg with generated questions
and ground truth "must contain" labels for evaluating retrieval accuracy.
"""

import pandas as pd
import numpy as np
import torch
import os
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from transformers import AutoTokenizer, AutoModel
from hybrid_retriever import HybridRetriever
import tempfile
import json

@dataclass
class RetrievalResult:
    """Results from retrieval evaluation."""
    dcg_at_1: float
    dcg_at_2: float
    dcg_at_5: float
    dcg_at_10: float
    dcg_at_20: float
    total_questions: int
    correct_retrievals: int
    book_name: str
    retrieval_method: str
    top_k_tested: int

class GutenQAEvaluator:
    """Evaluates retrieval performance using GutenQA dataset."""
    
    def __init__(self, data_dir: str = "./retrieval_evaluation_data"):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        
        # Initialize retriever (will use your existing hybrid retriever)
        try:
            self.hybrid_retriever = HybridRetriever(qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"))
        except Exception as e:
            self.logger.warning(f"Could not initialize HybridRetriever: {e}")
            self.hybrid_retriever = None
        
        # Initialize baseline retriever for comparison
        self.baseline_tokenizer = None
        self.baseline_model = None
        self._load_baseline_model()
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Dataset cache
        self.chunks_data = None
        self.questions_data = None
    
    def _load_baseline_model(self):
        """Load baseline Contriever model for comparison."""
        try:
            self.logger.info("Loading baseline Contriever model...")
            self.baseline_tokenizer = AutoTokenizer.from_pretrained('facebook/contriever')
            self.baseline_model = AutoModel.from_pretrained('facebook/contriever')
            self.logger.info("Baseline model loaded successfully")
        except Exception as e:
            self.logger.warning(f"Could not load baseline model: {e}")
    
    def load_gutenqa_dataset(self, force_download: bool = False) -> bool:
        """Load GutenQA dataset from HuggingFace."""
        try:
            chunks_path = os.path.join(self.data_dir, "gutenqa_chunks.parquet")
            questions_path = os.path.join(self.data_dir, "gutenqa_questions.parquet")
            
            # Check if already cached
            if not force_download and os.path.exists(chunks_path) and os.path.exists(questions_path):
                self.logger.info("Loading cached GutenQA dataset...")
                self.chunks_data = pd.read_parquet(chunks_path)
                self.questions_data = pd.read_parquet(questions_path)
                self.logger.info(f"Loaded {len(self.chunks_data)} chunks and {len(self.questions_data)} questions from cache")
                return True
            
            # Download from HuggingFace
            self.logger.info("Downloading GutenQA dataset from HuggingFace...")
            
            self.chunks_data = pd.read_parquet("hf://datasets/LumberChunker/GutenQA/gutenqa_chunks.parquet")
            self.questions_data = pd.read_parquet("hf://datasets/LumberChunker/GutenQA/questions.parquet")
            
            # Cache the data
            self.chunks_data.to_parquet(chunks_path)
            self.questions_data.to_parquet(questions_path)
            
            self.logger.info(f"Downloaded and cached {len(self.chunks_data)} chunks and {len(self.questions_data)} questions")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load GutenQA dataset: {e}")
            return False
    
    def get_available_books(self) -> List[str]:
        """Get list of available books in the dataset."""
        if self.chunks_data is None:
            return []
        return sorted(self.chunks_data['Book Name'].unique().tolist())
    
    def mean_pooling(self, token_embeddings, mask):
        """Mean pooling for sentence embeddings."""
        token_embeddings = token_embeddings.masked_fill(~mask[..., None].bool(), 0.)
        sentence_embeddings = token_embeddings.sum(dim=1) / mask.sum(dim=1)[..., None]
        return sentence_embeddings
    
    def compute_dcg(self, relevance_list: List[int]) -> float:
        """Compute Discounted Cumulative Gain."""
        dcg = 0.0
        for i in range(1, len(relevance_list) + 1):
            dcg += (np.power(2, relevance_list[i-1]) - 1) / np.log2(i + 1)
        return dcg
    
    def find_relevance_labels(self, retrieved_chunks: List[str], gold_label: str) -> List[int]:
        """Find which retrieved chunks contain the gold label."""
        relevance = []
        gold_label = gold_label.lower()
        
        for chunk in retrieved_chunks:
            if gold_label in chunk.lower():
                relevance.append(1)
                # Once we find a match, rest are 0
                relevance.extend([0] * (len(retrieved_chunks) - len(relevance)))
                break
            else:
                relevance.append(0)
        
        return relevance
    
    def evaluate_baseline_retrieval(self, book_name: str, max_questions: Optional[int] = None) -> RetrievalResult:
        """Evaluate retrieval using baseline Contriever model."""
        if self.baseline_model is None:
            raise ValueError("Baseline model not available")
        
        # Filter data for specific book
        book_chunks = self.chunks_data[self.chunks_data['Book Name'] == book_name].reset_index(drop=True)
        book_questions = self.questions_data[self.questions_data['Book Name'] == book_name].reset_index(drop=True)
        
        if max_questions:
            book_questions = book_questions.head(max_questions)
        
        self.logger.info(f"Evaluating baseline retrieval on {book_name}: {len(book_chunks)} chunks, {len(book_questions)} questions")
        
        # Tokenize chunks and questions
        inputs_chunks = self.baseline_tokenizer(
            book_chunks["Chunk"].tolist(), 
            padding=True, 
            truncation=True, 
            return_tensors='pt',
            max_length=512
        )
        inputs_questions = self.baseline_tokenizer(
            book_questions["Question"].tolist(), 
            padding=True, 
            truncation=True, 
            return_tensors='pt',
            max_length=512
        )
        
        # Compute embeddings
        with torch.no_grad():
            outputs_chunks = self.baseline_model(**inputs_chunks)
            outputs_questions = self.baseline_model(**inputs_questions)
        
        embeddings_chunks = self.mean_pooling(outputs_chunks[0], inputs_chunks['attention_mask']).detach().cpu().numpy()
        embeddings_questions = self.mean_pooling(outputs_questions[0], inputs_questions['attention_mask']).detach().cpu().numpy()
        
        # Calculate DCG@k for different k values
        dcg_scores = {k: [] for k in [1, 2, 5, 10, 20]}
        correct_retrievals = 0
        
        for i, question_embedding in enumerate(embeddings_questions):
            gold_label = book_questions.loc[i, "Chunk Must Contain"]
            
            # Calculate similarities
            similarities = np.dot(embeddings_chunks, question_embedding)
            
            # For each k, get top-k results and compute DCG
            for k in [1, 2, 5, 10, 20]:
                top_k = min(k, len(book_chunks))
                top_indices = np.argsort(similarities)[-top_k:][::-1]
                retrieved_chunks = [book_chunks.loc[idx, "Chunk"] for idx in top_indices]
                
                relevance = self.find_relevance_labels(retrieved_chunks, gold_label)
                dcg = self.compute_dcg(relevance)
                dcg_scores[k].append(dcg)
                
                # Count correct retrievals at top-1
                if k == 1 and relevance[0] == 1:
                    correct_retrievals += 1
        
        return RetrievalResult(
            dcg_at_1=float(np.mean(dcg_scores[1])),
            dcg_at_2=float(np.mean(dcg_scores[2])),
            dcg_at_5=float(np.mean(dcg_scores[5])),
            dcg_at_10=float(np.mean(dcg_scores[10])),
            dcg_at_20=float(np.mean(dcg_scores[20])),
            total_questions=len(book_questions),
            correct_retrievals=correct_retrievals,
            book_name=book_name,
            retrieval_method="contriever_baseline",
            top_k_tested=20
        )
    
    def evaluate_hybrid_retrieval(self, book_name: str, max_questions: Optional[int] = None) -> RetrievalResult:
        """Evaluate retrieval using your hybrid retriever."""
        if self.hybrid_retriever is None:
            raise ValueError("Hybrid retriever not available")
        
        # Filter data for specific book
        book_chunks = self.chunks_data[self.chunks_data['Book Name'] == book_name].reset_index(drop=True)
        book_questions = self.questions_data[self.questions_data['Book Name'] == book_name].reset_index(drop=True)
        
        if max_questions:
            book_questions = book_questions.head(max_questions)
        
        self.logger.info(f"Evaluating hybrid retrieval on {book_name}: {len(book_chunks)} chunks, {len(book_questions)} questions")
        
        # First, we need to add the book chunks to the hybrid retriever
        # Convert chunks to DocumentChunk format
        from document_processor import DocumentChunk
        
        temp_chunks = []
        for idx, row in book_chunks.iterrows():
            chunk = DocumentChunk(
                chunk_id=f"{book_name}_{idx}",
                text=row["Chunk"],
                source_file=book_name,
                page_number=0,
                section_header=row.get("Chapter", ""),
                chunk_index=idx,
                metadata={"book_name": book_name, "chapter": row.get("Chapter", "")}
            )
            temp_chunks.append(chunk)
        
        # Add chunks to retriever (temporarily)
        self.hybrid_retriever.add_documents(temp_chunks)
        
        # Calculate DCG@k for different k values
        dcg_scores = {k: [] for k in [1, 2, 5, 10, 20]}
        correct_retrievals = 0
        
        for i, row in book_questions.iterrows():
            question = row["Question"]
            gold_label = row["Chunk Must Contain"]
            
            # For each k, get top-k results and compute DCG
            for k in [1, 2, 5, 10, 20]:
                top_k = min(k, len(book_chunks))
                
                # Retrieve using hybrid retriever
                results = self.hybrid_retriever.retrieve(question, top_k=top_k)
                retrieved_chunks = [result.content for result in results]
                
                relevance = self.find_relevance_labels(retrieved_chunks, gold_label)
                dcg = self.compute_dcg(relevance)
                dcg_scores[k].append(dcg)
                
                # Count correct retrievals at top-1
                if k == 1 and len(relevance) > 0 and relevance[0] == 1:
                    correct_retrievals += 1
        
        return RetrievalResult(
            dcg_at_1=float(np.mean(dcg_scores[1])),
            dcg_at_2=float(np.mean(dcg_scores[2])),
            dcg_at_5=float(np.mean(dcg_scores[5])),
            dcg_at_10=float(np.mean(dcg_scores[10])),
            dcg_at_20=float(np.mean(dcg_scores[20])),
            total_questions=len(book_questions),
            correct_retrievals=correct_retrievals,
            book_name=book_name,
            retrieval_method="hybrid_retriever",
            top_k_tested=20
        )
    
    def compare_retrievers(self, book_name: str, max_questions: Optional[int] = None) -> Dict[str, RetrievalResult]:
        """Compare baseline and hybrid retrievers on the same book."""
        results = {}
        
        try:
            baseline_result = self.evaluate_baseline_retrieval(book_name, max_questions)
            results["baseline"] = baseline_result
        except Exception as e:
            self.logger.error(f"Baseline evaluation failed: {e}")
        
        try:
            hybrid_result = self.evaluate_hybrid_retrieval(book_name, max_questions)
            results["hybrid"] = hybrid_result
        except Exception as e:
            self.logger.error(f"Hybrid evaluation failed: {e}")
        
        return results
    
    def evaluate_multiple_books(self, book_names: List[str], max_questions_per_book: Optional[int] = None) -> Dict[str, Dict[str, RetrievalResult]]:
        """Evaluate retrieval performance across multiple books."""
        all_results = {}
        
        for book_name in book_names:
            self.logger.info(f"Evaluating book: {book_name}")
            book_results = self.compare_retrievers(book_name, max_questions_per_book)
            all_results[book_name] = book_results
        
        return all_results
    
    def get_dataset_statistics(self) -> Dict:
        """Get statistics about the GutenQA dataset."""
        if self.chunks_data is None or self.questions_data is None:
            return {}
        
        return {
            "total_books": len(self.chunks_data['Book Name'].unique()),
            "total_chunks": len(self.chunks_data),
            "total_questions": len(self.questions_data),
            "average_chunks_per_book": len(self.chunks_data) / len(self.chunks_data['Book Name'].unique()),
            "average_questions_per_book": len(self.questions_data) / len(self.questions_data['Book Name'].unique()),
            "available_books": self.get_available_books()[:10]  # Show first 10 books
        }

def format_retrieval_report(results: Dict[str, Dict[str, RetrievalResult]]) -> str:
    """Format retrieval evaluation results into a readable report."""
    report = []
    report.append("=" * 60)
    report.append("GUTENQA RETRIEVAL EVALUATION REPORT")
    report.append("=" * 60)
    
    # Overall statistics
    all_baseline_dcg1 = []
    all_hybrid_dcg1 = []
    all_baseline_dcg10 = []
    all_hybrid_dcg10 = []
    
    for book_name, book_results in results.items():
        report.append(f"\nBook: {book_name}")
        report.append("-" * 40)
        
        for method, result in book_results.items():
            report.append(f"Method: {result.retrieval_method}")
            report.append(f"Questions: {result.total_questions}")
            report.append(f"Correct@1: {result.correct_retrievals}/{result.total_questions} ({result.correct_retrievals/result.total_questions*100:.1f}%)")
            report.append(f"DCG@1: {result.dcg_at_1:.4f}")
            report.append(f"DCG@2: {result.dcg_at_2:.4f}")
            report.append(f"DCG@5: {result.dcg_at_5:.4f}")
            report.append(f"DCG@10: {result.dcg_at_10:.4f}")
            report.append(f"DCG@20: {result.dcg_at_20:.4f}")
            report.append("")
            
            # Collect for overall stats
            if method == "baseline":
                all_baseline_dcg1.append(result.dcg_at_1)
                all_baseline_dcg10.append(result.dcg_at_10)
            elif method == "hybrid":
                all_hybrid_dcg1.append(result.dcg_at_1)
                all_hybrid_dcg10.append(result.dcg_at_10)
    
    # Overall comparison
    if all_baseline_dcg1 and all_hybrid_dcg1:
        report.append("=" * 60)
        report.append("OVERALL COMPARISON")
        report.append("=" * 60)
        report.append(f"Average DCG@1 - Baseline: {np.mean(all_baseline_dcg1):.4f}")
        report.append(f"Average DCG@1 - Hybrid: {np.mean(all_hybrid_dcg1):.4f}")
        report.append(f"Average DCG@10 - Baseline: {np.mean(all_baseline_dcg10):.4f}")
        report.append(f"Average DCG@10 - Hybrid: {np.mean(all_hybrid_dcg10):.4f}")
        
        improvement_dcg1 = (np.mean(all_hybrid_dcg1) - np.mean(all_baseline_dcg1)) / np.mean(all_baseline_dcg1) * 100
        improvement_dcg10 = (np.mean(all_hybrid_dcg10) - np.mean(all_baseline_dcg10)) / np.mean(all_baseline_dcg10) * 100
        
        report.append(f"Improvement DCG@1: {improvement_dcg1:.1f}%")
        report.append(f"Improvement DCG@10: {improvement_dcg10:.1f}%")
    
    return "\n".join(report) 