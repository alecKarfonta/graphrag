import json
import numpy as np
import requests
import tarfile
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re
from semantic_chunker import SemanticChunker
import logging

@dataclass
class EvaluationResult:
    """Results from chunking evaluation."""
    precision: float
    recall: float
    f1_score: float
    total_documents: int
    total_boundaries: int
    correct_boundaries: int
    dataset_name: str
    chunking_method: str

class WikiSectionEvaluator:
    """Evaluates chunking performance using WikiSection dataset."""
    
    def __init__(self, data_dir: str = "./evaluation_data"):
        self.data_dir = data_dir
        self.semantic_chunker = SemanticChunker()
        self.logger = logging.getLogger(__name__)
        
        # Dataset URLs
        self.dataset_urls = {
            "wikisection_json": "https://github.com/sebastianarnold/WikiSection/raw/master/wikisection_dataset_json.tar.gz"
        }
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def download_dataset(self, force_download: bool = False) -> bool:
        """Download WikiSection dataset if not already present."""
        dataset_file = os.path.join(self.data_dir, "wikisection_dataset_json.tar.gz")
        extracted_dir = os.path.join(self.data_dir, "wikisection")
        
        # Check if already downloaded and extracted
        if os.path.exists(extracted_dir) and not force_download:
            self.logger.info("WikiSection dataset already available")
            return True
        
        try:
            self.logger.info("Downloading WikiSection dataset...")
            response = requests.get(self.dataset_urls["wikisection_json"], stream=True)
            response.raise_for_status()
            
            # Save the file
            with open(dataset_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract the tar.gz file
            self.logger.info("Extracting dataset...")
            with tarfile.open(dataset_file, 'r:gz') as tar:
                tar.extractall(self.data_dir)
            
            # Rename extracted directory to standard name
            if os.path.exists(os.path.join(self.data_dir, "wikisection_dataset_json")):
                os.rename(
                    os.path.join(self.data_dir, "wikisection_dataset_json"),
                    extracted_dir
                )
            
            self.logger.info("Dataset downloaded and extracted successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download dataset: {e}")
            return False
    
    def load_wikisection_data(self, subset: str = "en_disease") -> List[Dict]:
        """Load WikiSection dataset subset."""
        # Try multiple possible file paths/names
        possible_paths = [
            os.path.join(self.data_dir, "wikisection", f"{subset}.json"),
            os.path.join(self.data_dir, f"wikisection_{subset}_train.json"),
            os.path.join(self.data_dir, f"wikisection_{subset}_test.json"),
            os.path.join(self.data_dir, f"wikisection_{subset}_validation.json")
        ]
        
        for dataset_path in possible_paths:
            if os.path.exists(dataset_path):
                try:
                    with open(dataset_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.logger.info(f"Loaded {len(data)} documents from {dataset_path}")
                    return data
                    
                except Exception as e:
                    self.logger.error(f"Failed to load dataset from {dataset_path}: {e}")
                    continue
        
        self.logger.error(f"No dataset file found for subset: {subset}")
        self.logger.error(f"Searched paths: {possible_paths}")
        return []
    
    def evaluate_chunking(self, documents: List[Dict], sample_size: Optional[int] = None) -> EvaluationResult:
        """Evaluate chunking performance against WikiSection ground truth."""
        if sample_size:
            documents = documents[:sample_size]
        
        all_precision = []
        all_recall = []
        all_f1 = []
        total_boundaries = 0
        correct_boundaries = 0
        
        self.logger.info(f"Evaluating chunking on {len(documents)} documents...")
        
        for i, doc in enumerate(documents):
            if i % 10 == 0:
                self.logger.info(f"Processing document {i+1}/{len(documents)}")
            
            try:
                # Extract plain text and ground truth boundaries
                plain_text, ground_truth_boundaries = self._prepare_document(doc)
                
                if not plain_text.strip():
                    continue
                
                # Apply semantic chunker
                predicted_chunks = self.semantic_chunker.create_semantic_chunks(plain_text)
                predicted_boundaries = self._get_predicted_boundaries(predicted_chunks, plain_text)
                
                # Calculate boundary-based metrics
                precision, recall, f1, correct, total = self._calculate_boundary_metrics(
                    ground_truth_boundaries, predicted_boundaries
                )
                
                all_precision.append(precision)
                all_recall.append(recall)
                all_f1.append(f1)
                total_boundaries += total
                correct_boundaries += correct
                
            except Exception as e:
                self.logger.warning(f"Failed to process document {i}: {e}")
                continue
        
        if not all_precision:
            raise ValueError("No documents could be processed successfully")
        
        return EvaluationResult(
            precision=float(np.mean(all_precision)),
            recall=float(np.mean(all_recall)),
            f1_score=float(np.mean(all_f1)),
            total_documents=len(documents),
            total_boundaries=total_boundaries,
            correct_boundaries=correct_boundaries,
            dataset_name="WikiSection",
            chunking_method="semantic"
        )
    
    def _prepare_document(self, doc: Dict) -> Tuple[str, List[int]]:
        """Prepare document by extracting plain text and ground truth boundaries."""
        # WikiSection format: documents have 'text' and 'annotations'
        full_text = doc.get('text', '')
        annotations = doc.get('annotations', [])
        
        # Extract section boundaries from annotations
        boundaries = []
        for annotation in annotations:
            begin_pos = annotation.get('begin', 0)
            boundaries.append(begin_pos)
        
        # Sort boundaries
        boundaries = sorted(list(set(boundaries)))
        
        return full_text, boundaries
    
    def _get_predicted_boundaries(self, chunks: List[str], original_text: str) -> List[int]:
        """Get character positions where chunks begin in the original text."""
        boundaries = [0]  # Always start at position 0
        current_pos = 0
        
        for chunk in chunks[:-1]:  # Don't include the last chunk end
            # Find the chunk in the original text starting from current_pos
            chunk_start = original_text.find(chunk.strip()[:50], current_pos)
            if chunk_start != -1:
                chunk_end = chunk_start + len(chunk)
                boundaries.append(chunk_end)
                current_pos = chunk_end
            else:
                # Fallback: estimate position based on chunk lengths
                current_pos += len(chunk)
                boundaries.append(current_pos)
        
        return sorted(list(set(boundaries)))
    
    def _calculate_boundary_metrics(self, ground_truth: List[int], predicted: List[int], 
                                  tolerance: int = 10) -> Tuple[float, float, float, int, int]:
        """Calculate precision, recall, and F1 for boundary detection with tolerance."""
        if not ground_truth or not predicted:
            return 0.0, 0.0, 0.0, 0, len(ground_truth)
        
        # Remove boundary at position 0 as it's trivial
        gt_boundaries = [b for b in ground_truth if b > 0]
        pred_boundaries = [b for b in predicted if b > 0]
        
        if not gt_boundaries:
            return 0.0, 0.0, 0.0, 0, 0
        
        # Count true positives with tolerance
        true_positives = 0
        for pred_boundary in pred_boundaries:
            if any(abs(pred_boundary - gt_boundary) <= tolerance 
                   for gt_boundary in gt_boundaries):
                true_positives += 1
        
        # Calculate metrics
        precision = true_positives / len(pred_boundaries) if pred_boundaries else 0.0
        recall = true_positives / len(gt_boundaries) if gt_boundaries else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return precision, recall, f1, true_positives, len(gt_boundaries)
    
    def run_comparative_evaluation(self, subsets: Optional[List[str]] = None, sample_size: int = 50) -> Dict[str, EvaluationResult]:
        """Run evaluation on multiple WikiSection subsets."""
        if subsets is None:
            subsets = ["en_disease", "en_city", "de_disease", "de_city"]
        
        results = {}
        
        for subset in subsets:
            self.logger.info(f"Evaluating on subset: {subset}")
            
            documents = self.load_wikisection_data(subset)
            if not documents:
                self.logger.warning(f"No documents loaded for subset: {subset}")
                continue
            
            try:
                result = self.evaluate_chunking(documents, sample_size=sample_size)
                result.dataset_name = f"WikiSection-{subset}"
                results[subset] = result
                
                self.logger.info(f"Results for {subset}: P={result.precision:.3f}, R={result.recall:.3f}, F1={result.f1_score:.3f}")
                
            except Exception as e:
                self.logger.error(f"Evaluation failed for subset {subset}: {e}")
        
        return results
    
    def compare_with_baseline(self, documents: List[Dict], baseline_chunk_size: int = 500) -> Dict[str, EvaluationResult]:
        """Compare semantic chunking with fixed-size baseline."""
        # Test semantic chunking
        semantic_result = self.evaluate_chunking(documents)
        semantic_result.chunking_method = "semantic"
        
        # Test fixed-size chunking
        baseline_result = self._evaluate_fixed_size_chunking(documents, baseline_chunk_size)
        baseline_result.chunking_method = f"fixed-size-{baseline_chunk_size}"
        
        return {
            "semantic": semantic_result,
            "baseline": baseline_result
        }
    
    def _evaluate_fixed_size_chunking(self, documents: List[Dict], chunk_size: int) -> EvaluationResult:
        """Evaluate fixed-size chunking as baseline."""
        all_precision = []
        all_recall = []
        all_f1 = []
        total_boundaries = 0
        correct_boundaries = 0
        
        for doc in documents:
            try:
                plain_text, ground_truth_boundaries = self._prepare_document(doc)
                
                if not plain_text.strip():
                    continue
                
                # Create fixed-size chunks
                chunks = self._create_fixed_size_chunks(plain_text, chunk_size)
                predicted_boundaries = self._get_predicted_boundaries(chunks, plain_text)
                
                # Calculate metrics
                precision, recall, f1, correct, total = self._calculate_boundary_metrics(
                    ground_truth_boundaries, predicted_boundaries
                )
                
                all_precision.append(precision)
                all_recall.append(recall)
                all_f1.append(f1)
                total_boundaries += total
                correct_boundaries += correct
                
            except Exception as e:
                continue
        
        return EvaluationResult(
            precision=float(np.mean(all_precision)) if all_precision else 0.0,
            recall=float(np.mean(all_recall)) if all_recall else 0.0,
            f1_score=float(np.mean(all_f1)) if all_f1 else 0.0,
            total_documents=len(documents),
            total_boundaries=total_boundaries,
            correct_boundaries=correct_boundaries,
            dataset_name="WikiSection",
            chunking_method="fixed-size"
        )
    
    def _create_fixed_size_chunks(self, text: str, chunk_size: int) -> List[str]:
        """Create fixed-size chunks for baseline comparison."""
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

def format_evaluation_report(results: Dict[str, EvaluationResult]) -> str:
    """Format evaluation results into a readable report."""
    report = []
    report.append("=" * 60)
    report.append("WIKISECTION CHUNKING EVALUATION REPORT")
    report.append("=" * 60)
    
    for subset_name, result in results.items():
        report.append(f"\nDataset: {result.dataset_name}")
        report.append(f"Method: {result.chunking_method}")
        report.append(f"Documents: {result.total_documents}")
        report.append(f"Precision: {result.precision:.4f}")
        report.append(f"Recall: {result.recall:.4f}")
        report.append(f"F1-Score: {result.f1_score:.4f}")
        report.append(f"Boundary Accuracy: {result.correct_boundaries}/{result.total_boundaries} ({result.correct_boundaries/result.total_boundaries*100:.2f}%)")
        report.append("-" * 40)
    
    return "\n".join(report) 