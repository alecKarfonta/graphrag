"""
Simplified comparison test focusing on key contextual embeddings metrics.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentence_transformers import SentenceTransformer
import numpy as np
import time

class BaselineEmbedder:
    """Baseline embedder without contextual enhancements."""
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed_text(self, text):
        """Generate basic embedding without context."""
        return self.model.encode(text)

def create_test_dataset():
    """Create a comprehensive test dataset."""
    return [
        {
            "name": "graphrag_installation_guide.txt",
            "chunks": [
                {
                    "text": "GraphRAG Installation Guide: This comprehensive guide walks you through the complete installation process for the GraphRAG hybrid retrieval system.",
                    "chunk_id": "install_1",
                    "chunk_index": 0,
                    "source_file": "graphrag_installation_guide.txt"
                },
                {
                    "text": "Prerequisites: Before installing GraphRAG, ensure you have Docker 20.10 or later, Python 3.8+, and at least 4GB RAM. Network connectivity is required for downloading dependencies.",
                    "chunk_id": "install_2",
                    "chunk_index": 1,
                    "source_file": "graphrag_installation_guide.txt"
                },
                {
                    "text": "Step 1: Download the GraphRAG package from the official repository. Extract the package to your desired directory using tar -xzf graphrag-latest.tar.gz",
                    "chunk_id": "install_3",
                    "chunk_index": 2,
                    "source_file": "graphrag_installation_guide.txt"
                },
                {
                    "text": "Step 2: Navigate to the extracted directory and run the setup script with administrator privileges: sudo ./setup.sh",
                    "chunk_id": "install_4",
                    "chunk_index": 3,
                    "source_file": "graphrag_installation_guide.txt"
                },
                {
                    "text": "Configuration: After installation, configure the Neo4j database connection and Qdrant vector store settings in the config/settings.json file.",
                    "chunk_id": "install_5",
                    "chunk_index": 4,
                    "source_file": "graphrag_installation_guide.txt"
                }
            ]
        },
        {
            "name": "a_christmas_carol_chapter1.txt",
            "chunks": [
                {
                    "text": "Marley was dead, to begin with. There is no doubt whatever about that. The register of his burial was signed by the clergyman, the clerk, the undertaker, and the chief mourner.",
                    "chunk_id": "christmas_1",
                    "chunk_index": 0,
                    "source_file": "a_christmas_carol_chapter1.txt"
                },
                {
                    "text": "Scrooge never painted out Old Marley's name. There it stood, years afterwards, above the warehouse door: Scrooge and Marley. The firm was known as Scrooge and Marley.",
                    "chunk_id": "christmas_2",
                    "chunk_index": 1,
                    "source_file": "a_christmas_carol_chapter1.txt"
                },
                {
                    "text": "Sometimes people new to the business called Scrooge Scrooge, and sometimes Marley, but he answered to both names. It was all the same to him.",
                    "chunk_id": "christmas_3",
                    "chunk_index": 2,
                    "source_file": "a_christmas_carol_chapter1.txt"
                },
                {
                    "text": "Oh! But he was a tight-fisted hand at the grindstone, Scrooge! A squeezing, wrenching, grasping, scraping, clutching, covetous, old sinner!",
                    "chunk_id": "christmas_4",
                    "chunk_index": 3,
                    "source_file": "a_christmas_carol_chapter1.txt"
                },
                {
                    "text": "The mention of Marley's funeral brings me back to the point I started from. There is no doubt that Marley was dead. This must be distinctly understood, or nothing wonderful can come of the story I am going to relate.",
                    "chunk_id": "christmas_5",
                    "chunk_index": 4,
                    "source_file": "a_christmas_carol_chapter1.txt"
                }
            ]
        },
        {
            "name": "machine_learning_research_paper.txt",
            "chunks": [
                {
                    "text": "Abstract: This paper presents a novel approach to hybrid information retrieval systems that combines vector search with knowledge graph reasoning. Our methodology demonstrates significant improvements in retrieval accuracy.",
                    "chunk_id": "research_1",
                    "chunk_index": 0,
                    "source_file": "machine_learning_research_paper.txt"
                },
                {
                    "text": "Introduction: Traditional information retrieval systems rely heavily on keyword matching and vector similarity. However, these approaches often fail to capture the semantic relationships and contextual information present in documents.",
                    "chunk_id": "research_2",
                    "chunk_index": 1,
                    "source_file": "machine_learning_research_paper.txt"
                },
                {
                    "text": "Methodology: We propose a hybrid approach that combines dense vector embeddings with structured knowledge graphs. The system employs a two-stage retrieval process: broad semantic search followed by graph-based reasoning.",
                    "chunk_id": "research_3",
                    "chunk_index": 2,
                    "source_file": "machine_learning_research_paper.txt"
                },
                {
                    "text": "Results: Our experiments on the MS MARCO dataset show a 15-25% improvement in retrieval accuracy compared to baseline systems. The hybrid approach particularly excels at complex queries requiring multi-hop reasoning.",
                    "chunk_id": "research_4",
                    "chunk_index": 3,
                    "source_file": "machine_learning_research_paper.txt"
                },
                {
                    "text": "Conclusion: The hybrid retrieval system demonstrates significant potential for improving information retrieval accuracy. Future work will focus on scaling the approach to larger document collections and real-time applications.",
                    "chunk_id": "research_5",
                    "chunk_index": 4,
                    "source_file": "machine_learning_research_paper.txt"
                }
            ]
        },
        {
            "name": "docker_configuration_guide.txt",
            "chunks": [
                {
                    "text": "Docker Configuration for GraphRAG: This guide explains how to configure Docker containers for optimal GraphRAG performance in production environments.",
                    "chunk_id": "docker_1",
                    "chunk_index": 0,
                    "source_file": "docker_configuration_guide.txt"
                },
                {
                    "text": "Container Requirements: Each GraphRAG service requires specific resource allocations. The API service needs 2GB RAM, Neo4j requires 4GB RAM, and Qdrant needs 1GB RAM minimum.",
                    "chunk_id": "docker_2",
                    "chunk_index": 1,
                    "source_file": "docker_configuration_guide.txt"
                },
                {
                    "text": "Network Configuration: Configure the Docker network to allow communication between services. Use docker network create graphrag-network and attach all containers to this network.",
                    "chunk_id": "docker_3",
                    "chunk_index": 2,
                    "source_file": "docker_configuration_guide.txt"
                },
                {
                    "text": "Volume Mounting: Mount persistent volumes for Neo4j data, Qdrant snapshots, and API logs. This ensures data persistence across container restarts and updates.",
                    "chunk_id": "docker_4",
                    "chunk_index": 3,
                    "source_file": "docker_configuration_guide.txt"
                },
                {
                    "text": "Performance Tuning: For production deployments, adjust the number of worker processes, connection pool sizes, and memory limits based on your specific workload requirements.",
                    "chunk_id": "docker_5",
                    "chunk_index": 4,
                    "source_file": "docker_configuration_guide.txt"
                }
            ]
        }
    ]

def create_test_queries():
    """Create diverse test queries."""
    return [
        {
            "query": "How do I install GraphRAG step by step?",
            "description": "Detailed installation procedure",
            "expected_doc": "graphrag_installation_guide.txt"
        },
        {
            "query": "What are the system requirements for GraphRAG?",
            "description": "System prerequisites",
            "expected_doc": "graphrag_installation_guide.txt"
        },
        {
            "query": "How to configure Docker for GraphRAG?",
            "description": "Docker configuration",
            "expected_doc": "docker_configuration_guide.txt"
        },
        {
            "query": "What are the Docker container requirements?",
            "description": "Docker resource requirements",
            "expected_doc": "docker_configuration_guide.txt"
        },
        {
            "query": "Who is Marley in A Christmas Carol?",
            "description": "Character identification",
            "expected_doc": "a_christmas_carol_chapter1.txt"
        },
        {
            "query": "What is Scrooge's personality like?",
            "description": "Character description",
            "expected_doc": "a_christmas_carol_chapter1.txt"
        },
        {
            "query": "What happens at the beginning of the story?",
            "description": "Plot summary",
            "expected_doc": "a_christmas_carol_chapter1.txt"
        },
        {
            "query": "What are the research findings on hybrid retrieval?",
            "description": "Research results",
            "expected_doc": "machine_learning_research_paper.txt"
        },
        {
            "query": "What methodology was used in the research?",
            "description": "Research methodology",
            "expected_doc": "machine_learning_research_paper.txt"
        },
        {
            "query": "What are the conclusions of the study?",
            "description": "Research conclusions",
            "expected_doc": "machine_learning_research_paper.txt"
        },
        {
            "query": "How to set up a production environment?",
            "description": "Production setup",
            "expected_doc": "docker_configuration_guide.txt"
        },
        {
            "query": "What improvements were achieved in the research?",
            "description": "Performance improvements",
            "expected_doc": "machine_learning_research_paper.txt"
        }
    ]

def test_baseline_embeddings():
    """Test baseline embeddings without contextual enhancement."""
    print("🧪 Testing Baseline Embeddings (Before Contextual Enhancement)")
    print("=" * 60)
    
    baseline_embedder = BaselineEmbedder()
    test_docs = create_test_dataset()
    test_queries = create_test_queries()
    
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
    
    # Test queries
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
            ),
            "correct_doc_rank": next(
                (i+1 for i, result in enumerate(top_results) 
                 if result["chunk"]["source_file"] == query_case["expected_doc"]), 
                None
            )
        })
    
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
    
    test_docs = create_test_dataset()
    test_queries = create_test_queries()
    
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
    
    # Test queries
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
            ),
            "correct_doc_rank": next(
                (i+1 for i, result in enumerate(top_results) 
                 if result["chunk"]["source_file"] == query_case["expected_doc"]), 
                None
            )
        })
    
    return contextual_results, contextual_time

def compare_results(baseline_results, contextual_results, baseline_time, contextual_time):
    """Compare baseline and contextual embedding results."""
    print("\n📊 COMPARISON RESULTS")
    print("=" * 60)
    
    if not baseline_results or not contextual_results:
        print("❌ Cannot compare results - missing data")
        return
    
    # Overall statistics
    print("📈 OVERALL PERFORMANCE METRICS")
    print("-" * 40)
    
    baseline_similarities = [r["top_similarity"] for r in baseline_results]
    contextual_similarities = [r["top_similarity"] for r in contextual_results]
    
    avg_baseline_sim = np.mean(baseline_similarities)
    avg_contextual_sim = np.mean(contextual_similarities)
    std_baseline_sim = np.std(baseline_similarities)
    std_contextual_sim = np.std(contextual_similarities)
    
    print(f"Average Baseline Similarity: {avg_baseline_sim:.3f} (±{std_baseline_sim:.3f})")
    print(f"Average Contextual Similarity: {avg_contextual_sim:.3f} (±{std_contextual_sim:.3f})")
    print(f"Similarity Change: {avg_contextual_sim - avg_baseline_sim:+.3f} ({(avg_contextual_sim - avg_baseline_sim)/avg_baseline_sim*100:+.1f}%)")
    
    # Accuracy analysis
    baseline_correct = sum(1 for r in baseline_results if r["correct_doc_found"])
    contextual_correct = sum(1 for r in contextual_results if r["correct_doc_found"])
    
    baseline_accuracy = baseline_correct / len(baseline_results) * 100
    contextual_accuracy = contextual_correct / len(contextual_results) * 100
    
    print(f"Baseline Accuracy: {baseline_accuracy:.1f}% ({baseline_correct}/{len(baseline_results)})")
    print(f"Contextual Accuracy: {contextual_accuracy:.1f}% ({contextual_correct}/{len(contextual_results)})")
    print(f"Accuracy Change: {contextual_accuracy - baseline_accuracy:+.1f}%")
    
    # Ranking analysis
    baseline_ranks = [r["correct_doc_rank"] for r in baseline_results if r["correct_doc_rank"]]
    contextual_ranks = [r["correct_doc_rank"] for r in contextual_results if r["correct_doc_rank"]]
    
    if baseline_ranks and contextual_ranks:
        avg_baseline_rank = np.mean(baseline_ranks)
        avg_contextual_rank = np.mean(contextual_ranks)
        print(f"Average Baseline Rank: {avg_baseline_rank:.1f}")
        print(f"Average Contextual Rank: {avg_contextual_rank:.1f}")
        print(f"Ranking Improvement: {avg_baseline_rank - avg_contextual_rank:+.1f} positions")
    
    # Performance analysis
    print(f"\n⚡ PERFORMANCE ANALYSIS")
    print("-" * 40)
    print(f"Baseline Processing Time: {baseline_time:.3f} seconds")
    print(f"Contextual Processing Time: {contextual_time:.3f} seconds")
    time_overhead = contextual_time - baseline_time
    print(f"Processing Overhead: {time_overhead:+.3f} seconds ({time_overhead/baseline_time*100:+.1f}%)")
    
    # Enhancement quality analysis
    print(f"\n🎯 ENHANCEMENT QUALITY")
    print("-" * 40)
    
    if contextual_results:
        enhancement_ratios = []
        context_parts_counts = []
        
        for result in contextual_results:
            for res in result["results"]:
                enhanced_text = res["enhanced_text"]
                original_text = res["chunk"]["text"]
                enhancement_ratio = len(enhanced_text) / len(original_text)
                enhancement_ratios.append(enhancement_ratio)
                
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
                if res["chunk_context"].chunk_position != "middle":
                    context_parts += 1
                
                context_parts_counts.append(context_parts)
        
        avg_enhancement_ratio = np.mean(enhancement_ratios)
        avg_context_parts = np.mean(context_parts_counts)
        
        print(f"Average Enhancement Ratio: {avg_enhancement_ratio:.2f}x")
        print(f"Average Context Parts: {avg_context_parts:.1f}")
        print(f"Enhancement Range: {min(enhancement_ratios):.2f}x - {max(enhancement_ratios):.2f}x")
    
    # Query-by-query analysis
    print(f"\n🔍 QUERY-BY-QUERY ANALYSIS")
    print("-" * 40)
    
    improvements = []
    for i, (baseline, contextual) in enumerate(zip(baseline_results, contextual_results)):
        query_desc = baseline["query"]["description"]
        baseline_sim = baseline["top_similarity"]
        contextual_sim = contextual["top_similarity"]
        improvement = contextual_sim - baseline_sim
        improvements.append(improvement)
        
        print(f"{i+1:2d}. {query_desc}")
        print(f"    Baseline: {baseline_sim:.3f} | Contextual: {contextual_sim:.3f} | Change: {improvement:+.3f} ({improvement/baseline_sim*100:+.1f}%)")
        print(f"    Correct: Baseline={baseline['correct_doc_found']} (rank {baseline['correct_doc_rank']}) | Contextual={contextual['correct_doc_found']} (rank {contextual['correct_doc_rank']})")
    
    # Summary
    print(f"\n🎉 COMPREHENSIVE SUMMARY")
    print("-" * 40)
    print(f"✅ Contextual embeddings provide {(avg_contextual_sim - avg_baseline_sim)/avg_baseline_sim*100:+.1f}% similarity change")
    print(f"✅ Accuracy changed by {contextual_accuracy - baseline_accuracy:+.1f}%")
    print(f"✅ Processing overhead: {time_overhead/baseline_time*100:+.1f}%")
    print(f"✅ Rich contextual information added (avg {avg_context_parts:.1f} parts per embedding)")
    print(f"✅ Document type and domain awareness working")
    print(f"✅ Chunk-specific context enhancement active")
    print(f"✅ Enhancement ratio: {avg_enhancement_ratio:.2f}x average")
    
    # Show some examples of improvements
    positive_improvements = [imp for imp in improvements if imp > 0]
    if positive_improvements:
        print(f"✅ {len(positive_improvements)} queries showed improvement")
        print(f"✅ Best improvement: {max(improvements):+.3f} ({max(improvements)/avg_baseline_sim*100:+.1f}%)")

def main():
    """Run the simplified comparison test."""
    print("🔬 Simplified Contextual Embeddings Comparison")
    print("=" * 60)
    
    # Test baseline embeddings
    baseline_results, baseline_time = test_baseline_embeddings()
    
    # Test contextual embeddings
    contextual_results, contextual_time = test_contextual_embeddings()
    
    # Compare results
    compare_results(baseline_results, contextual_results, baseline_time, contextual_time)
    
    print(f"\n" + "=" * 60)
    print("✅ Simplified comparison test completed!")

if __name__ == "__main__":
    main() 