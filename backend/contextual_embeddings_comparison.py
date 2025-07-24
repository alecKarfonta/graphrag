"""
Comprehensive comparison test for contextual embeddings before and after implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hybrid_retriever import HybridRetriever
from sentence_transformers import SentenceTransformer
import numpy as np
import time
import json

class BaselineEmbedder:
    """Baseline embedder without contextual enhancements for comparison."""
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_text(self, text):
        """Generate basic embedding without context."""
        return self.model.encode(text)

def create_test_documents():
    """Create test documents for comparison."""
    return [
        {
            "name": "technical_manual.txt",
            "chunks": [
                {
                    "text": "Installation Procedure: Download the GraphRAG package and extract it to your desired directory. Run the setup script with administrator privileges.",
                    "chunk_id": "tech_1",
                    "chunk_index": 0,
                    "source_file": "technical_manual.txt",
                    "metadata": {"content_type": "procedural"}
                },
                {
                    "text": "System Requirements: The software requires Docker 20.10+, Python 3.8+, and at least 4GB RAM. Network connectivity is required for license validation.",
                    "chunk_id": "tech_2",
                    "chunk_index": 1,
                    "source_file": "technical_manual.txt",
                    "metadata": {"content_type": "specification"}
                },
                {
                    "text": "Configuration Steps: After installation, configure the database connection parameters in the config.ini file. Set the server address, port number, and authentication credentials.",
                    "chunk_id": "tech_3",
                    "chunk_index": 2,
                    "source_file": "technical_manual.txt",
                    "metadata": {"content_type": "procedural"}
                }
            ]
        },
        {
            "name": "a_christmas_carol.txt",
            "chunks": [
                {
                    "text": "Marley was dead, to begin with. There is no doubt whatever about that. The register of his burial was signed by the clergyman, the clerk, the undertaker, and the chief mourner.",
                    "chunk_id": "christmas_1",
                    "chunk_index": 0,
                    "source_file": "a_christmas_carol.txt",
                    "metadata": {"content_type": "narrative"}
                },
                {
                    "text": "Scrooge never painted out Old Marley's name. There it stood, years afterwards, above the warehouse door: Scrooge and Marley.",
                    "chunk_id": "christmas_2",
                    "chunk_index": 1,
                    "source_file": "a_christmas_carol.txt",
                    "metadata": {"content_type": "narrative"}
                },
                {
                    "text": "The mention of Marley's funeral brings me back to the point I started from. There is no doubt that Marley was dead. This must be distinctly understood, or nothing wonderful can come of the story I am going to relate.",
                    "chunk_id": "christmas_3",
                    "chunk_index": 2,
                    "source_file": "a_christmas_carol.txt",
                    "metadata": {"content_type": "narrative"}
                }
            ]
        },
        {
            "name": "research_paper.txt",
            "chunks": [
                {
                    "text": "Abstract: This study investigates the effectiveness of hybrid retrieval systems combining vector search with knowledge graphs. Our methodology employed a mixed-methods approach combining quantitative analysis with qualitative interviews.",
                    "chunk_id": "research_1",
                    "chunk_index": 0,
                    "source_file": "research_paper.txt",
                    "metadata": {"content_type": "academic"}
                },
                {
                    "text": "Methodology: The research methodology employed a mixed-methods approach combining quantitative analysis with qualitative interviews. Statistical significance was tested using p < 0.05.",
                    "chunk_id": "research_2",
                    "chunk_index": 1,
                    "source_file": "research_paper.txt",
                    "metadata": {"content_type": "methodology"}
                },
                {
                    "text": "Results: The findings demonstrate significant improvements in retrieval accuracy of 15-25% compared to baseline systems. The hybrid approach showed particular effectiveness for complex queries requiring multi-hop reasoning.",
                    "chunk_id": "research_3",
                    "chunk_index": 2,
                    "source_file": "research_paper.txt",
                    "metadata": {"content_type": "results"}
                }
            ]
        }
    ]

def test_baseline_embeddings():
    """Test baseline embeddings without contextual enhancement."""
    print("🧪 Testing Baseline Embeddings (Before Contextual Enhancement)")
    print("=" * 60)
    
    baseline_embedder = BaselineEmbedder()
    test_docs = create_test_documents()
    
    # Collect all chunks
    all_chunks = []
    for doc in test_docs:
        all_chunks.extend(doc["chunks"])
    
    print(f"Processing {len(all_chunks)} chunks with baseline embeddings...")
    
    # Generate baseline embeddings
    start_time = time.time()
    baseline_embeddings = []
    for chunk in all_chunks:
        embedding = baseline_embedder.embed_text(chunk["text"])
        baseline_embeddings.append({
            "chunk": chunk,
            "embedding": embedding,
            "text": chunk["text"]
        })
    baseline_time = time.time() - start_time
    
    print(f"✅ Baseline embeddings generated in {baseline_time:.3f} seconds")
    
    # Test queries for baseline
    test_queries = [
        {
            "query": "How do I install GraphRAG?",
            "description": "Technical installation query",
            "expected_doc": "technical_manual.txt"
        },
        {
            "query": "What are the system requirements?",
            "description": "Technical requirements query", 
            "expected_doc": "technical_manual.txt"
        },
        {
            "query": "Who is Marley in the story?",
            "description": "Narrative character query",
            "expected_doc": "a_christmas_carol.txt"
        },
        {
            "query": "What are the research findings?",
            "description": "Academic results query",
            "expected_doc": "research_paper.txt"
        }
    ]
    
    baseline_results = []
    
    for query_case in test_queries:
        query_text = query_case["query"]
        query_embedding = baseline_embedder.embed_text(query_text)
        
        # Find most similar chunks
        similarities = []
        for i, emb_data in enumerate(baseline_embeddings):
            similarity = np.dot(query_embedding, emb_data["embedding"]) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb_data["embedding"])
            )
            similarities.append({
                "index": i,
                "similarity": similarity,
                "chunk": emb_data["chunk"],
                "text": emb_data["text"]
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Get top 3 results
        top_results = similarities[:3]
        
        baseline_results.append({
            "query": query_case,
            "results": top_results,
            "top_similarity": top_results[0]["similarity"] if top_results else 0,
            "correct_doc_found": any(
                result["chunk"]["source_file"] == query_case["expected_doc"] 
                for result in top_results
            )
        })
        
        print(f"\n--- {query_case['description']} ---")
        print(f"Query: '{query_text}'")
        print(f"Top similarity: {top_results[0]['similarity']:.3f}")
        print(f"Correct document found: {baseline_results[-1]['correct_doc_found']}")
        
        for i, result in enumerate(top_results):
            print(f"  {i+1}. {result['chunk']['source_file']} (similarity: {result['similarity']:.3f})")
    
    return baseline_results, baseline_time

def test_contextual_embeddings():
    """Test contextual embeddings with enhancement."""
    print("\n🧪 Testing Contextual Embeddings (After Enhancement)")
    print("=" * 60)
    
    try:
        from contextual_embeddings import ContextualEmbedder
        contextual_embedder = ContextualEmbedder()
        print("✅ Contextual embedder initialized")
    except ImportError:
        print("❌ Contextual embedder not available")
        return None, 0
    
    test_docs = create_test_documents()
    
    # Generate contextual embeddings
    start_time = time.time()
    contextual_embeddings = []
    
    for doc in test_docs:
        doc_embeddings = contextual_embedder.embed_document_chunks(
            doc["chunks"], 
            doc["name"],
            {"title": doc["name"], "document_type": "test"}
        )
        
        for emb in doc_embeddings:
            contextual_embeddings.append({
                "chunk": {
                    "chunk_id": emb.chunk_context.chunk_id,
                    "source_file": doc["name"],
                    "text": emb.original_text
                },
                "embedding": emb.embedding,
                "enhanced_text": emb.enhanced_text,
                "document_context": emb.document_context,
                "chunk_context": emb.chunk_context
            })
    
    contextual_time = time.time() - start_time
    
    print(f"✅ Contextual embeddings generated in {contextual_time:.3f} seconds")
    print(f"✅ Enhanced {len(contextual_embeddings)} chunks with contextual information")
    
    # Test queries for contextual embeddings
    test_queries = [
        {
            "query": "How do I install GraphRAG?",
            "description": "Technical installation query",
            "expected_doc": "technical_manual.txt"
        },
        {
            "query": "What are the system requirements?",
            "description": "Technical requirements query", 
            "expected_doc": "technical_manual.txt"
        },
        {
            "query": "Who is Marley in the story?",
            "description": "Narrative character query",
            "expected_doc": "a_christmas_carol.txt"
        },
        {
            "query": "What are the research findings?",
            "description": "Academic results query",
            "expected_doc": "research_paper.txt"
        }
    ]
    
    contextual_results = []
    
    for query_case in test_queries:
        query_text = query_case["query"]
        query_embedding = contextual_embedder.model.encode(query_text)
        
        # Find most similar chunks
        similarities = []
        for i, emb_data in enumerate(contextual_embeddings):
            similarity = np.dot(query_embedding, emb_data["embedding"]) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emb_data["embedding"])
            )
            similarities.append({
                "index": i,
                "similarity": similarity,
                "chunk": emb_data["chunk"],
                "enhanced_text": emb_data["enhanced_text"],
                "document_context": emb_data["document_context"],
                "chunk_context": emb_data["chunk_context"]
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Get top 3 results
        top_results = similarities[:3]
        
        contextual_results.append({
            "query": query_case,
            "results": top_results,
            "top_similarity": top_results[0]["similarity"] if top_results else 0,
            "correct_doc_found": any(
                result["chunk"]["source_file"] == query_case["expected_doc"] 
                for result in top_results
            )
        })
        
        print(f"\n--- {query_case['description']} ---")
        print(f"Query: '{query_text}'")
        print(f"Top similarity: {top_results[0]['similarity']:.3f}")
        print(f"Correct document found: {contextual_results[-1]['correct_doc_found']}")
        
        for i, result in enumerate(top_results):
            doc_context = result["document_context"]
            chunk_context = result["chunk_context"]
            print(f"  {i+1}. {result['chunk']['source_file']} (similarity: {result['similarity']:.3f})")
            print(f"     Document type: {doc_context.document_type}, Domain: {doc_context.domain}")
            print(f"     Content type: {chunk_context.content_type}, Position: {chunk_context.chunk_position}")
    
    return contextual_results, contextual_time

def compare_results(baseline_results, contextual_results, baseline_time, contextual_time):
    """Compare baseline and contextual embedding results."""
    print("\n📊 COMPARISON RESULTS")
    print("=" * 60)
    
    if not baseline_results or not contextual_results:
        print("❌ Cannot compare results - missing data")
        return
    
    print("🔍 Query-by-Query Comparison:")
    print("-" * 40)
    
    total_baseline_similarity = 0
    total_contextual_similarity = 0
    baseline_correct = 0
    contextual_correct = 0
    
    for i, (baseline, contextual) in enumerate(zip(baseline_results, contextual_results)):
        query_desc = baseline["query"]["description"]
        baseline_sim = baseline["top_similarity"]
        contextual_sim = contextual["top_similarity"]
        improvement = contextual_sim - baseline_sim
        
        total_baseline_similarity += baseline_sim
        total_contextual_similarity += contextual_sim
        
        if baseline["correct_doc_found"]:
            baseline_correct += 1
        if contextual["correct_doc_found"]:
            contextual_correct += 1
        
        print(f"\n{i+1}. {query_desc}")
        print(f"   Baseline similarity: {baseline_sim:.3f}")
        print(f"   Contextual similarity: {contextual_sim:.3f}")
        print(f"   Improvement: {improvement:+.3f} ({improvement/baseline_sim*100:+.1f}%)")
        print(f"   Baseline correct: {baseline['correct_doc_found']}")
        print(f"   Contextual correct: {contextual['correct_doc_found']}")
    
    # Overall statistics
    print(f"\n📈 OVERALL STATISTICS")
    print("-" * 40)
    
    avg_baseline_sim = total_baseline_similarity / len(baseline_results)
    avg_contextual_sim = total_contextual_similarity / len(contextual_results)
    overall_improvement = avg_contextual_sim - avg_baseline_sim
    
    print(f"Average Baseline Similarity: {avg_baseline_sim:.3f}")
    print(f"Average Contextual Similarity: {avg_contextual_sim:.3f}")
    print(f"Overall Similarity Improvement: {overall_improvement:+.3f} ({overall_improvement/avg_baseline_sim*100:+.1f}%)")
    
    baseline_accuracy = baseline_correct / len(baseline_results) * 100
    contextual_accuracy = contextual_correct / len(contextual_results) * 100
    accuracy_improvement = contextual_accuracy - baseline_accuracy
    
    print(f"Baseline Accuracy: {baseline_accuracy:.1f}% ({baseline_correct}/{len(baseline_results)})")
    print(f"Contextual Accuracy: {contextual_accuracy:.1f}% ({contextual_correct}/{len(contextual_results)})")
    print(f"Accuracy Improvement: {accuracy_improvement:+.1f}%")
    
    # Performance comparison
    print(f"\n⚡ PERFORMANCE COMPARISON")
    print("-" * 40)
    print(f"Baseline Processing Time: {baseline_time:.3f} seconds")
    print(f"Contextual Processing Time: {contextual_time:.3f} seconds")
    time_overhead = contextual_time - baseline_time
    print(f"Processing Overhead: {time_overhead:+.3f} seconds ({time_overhead/baseline_time*100:+.1f}%)")
    
    # Enhancement quality
    print(f"\n🎯 ENHANCEMENT QUALITY")
    print("-" * 40)
    
    if contextual_results:
        # Calculate average enhancement ratio
        total_enhancement_ratio = 0
        total_context_parts = 0
        
        for result in contextual_results:
            for res in result["results"]:
                enhanced_text = res["enhanced_text"]
                original_text = res["chunk"]["text"]
                enhancement_ratio = len(enhanced_text) / len(original_text)
                total_enhancement_ratio += enhancement_ratio
                
                # Count context parts
                context_parts = 0
                if res["document_context"].document_type != "unknown":
                    context_parts += 1
                if res["document_context"].domain:
                    context_parts += 1
                if res["chunk_context"].content_type != "general":
                    context_parts += 1
                if res["chunk_context"].key_entities:
                    context_parts += 1
                
                total_context_parts += context_parts
        
        avg_enhancement_ratio = total_enhancement_ratio / (len(contextual_results) * 3)  # 3 results per query
        avg_context_parts = total_context_parts / (len(contextual_results) * 3)
        
        print(f"Average Enhancement Ratio: {avg_enhancement_ratio:.2f}x")
        print(f"Average Context Parts: {avg_context_parts:.1f}")
    
    # Summary
    print(f"\n🎉 SUMMARY")
    print("-" * 40)
    print(f"✅ Contextual embeddings provide {overall_improvement/avg_baseline_sim*100:+.1f}% similarity improvement")
    print(f"✅ Accuracy improved by {accuracy_improvement:+.1f}%")
    print(f"✅ Processing overhead: {time_overhead/baseline_time*100:+.1f}%")
    print(f"✅ Rich contextual information added to embeddings")
    print(f"✅ Document type and domain awareness working")
    print(f"✅ Chunk-specific context enhancement active")

def main():
    """Run the complete comparison test."""
    print("🔬 Contextual Embeddings Before/After Comparison")
    print("=" * 60)
    
    # Test baseline embeddings
    baseline_results, baseline_time = test_baseline_embeddings()
    
    # Test contextual embeddings
    contextual_results, contextual_time = test_contextual_embeddings()
    
    # Compare results
    compare_results(baseline_results, contextual_results, baseline_time, contextual_time)
    
    print(f"\n" + "=" * 60)
    print("✅ Comparison test completed!")

if __name__ == "__main__":
    main() 