"""
Test script for contextual embeddings integration with hybrid retriever.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hybrid_retriever import HybridRetriever
import json

def test_contextual_embeddings_integration():
    """Test that contextual embeddings integrate correctly with hybrid retriever."""
    print("Testing contextual embeddings integration with hybrid retriever...")
    
    try:
        # Initialize hybrid retriever
        retriever = HybridRetriever()
        print("✅ Hybrid retriever initialized")
        
        # Check if contextual embedder is available
        if hasattr(retriever, 'contextual_embedder') and retriever.contextual_embedder:
            print("✅ Contextual embedder is available")
        else:
            print("⚠️ Contextual embedder not available, using fallback")
        
        # Test chunks for different document types
        test_chunks = [
            {
                "text": "Installation Guide: This document provides step-by-step instructions for installing the GraphRAG system. The installation process requires Docker and approximately 2GB of disk space.",
                "chunk_id": "install_guide_1",
                "chunk_index": 0,
                "source_file": "installation_guide.txt",
                "metadata": {"content_type": "procedural", "section": "introduction"}
            },
            {
                "text": "System Requirements: The GraphRAG system requires Docker 20.10+, Python 3.8+, and at least 4GB RAM. Network connectivity is required for downloading models and dependencies.",
                "chunk_id": "install_guide_2",
                "chunk_index": 1,
                "source_file": "installation_guide.txt",
                "metadata": {"content_type": "specification", "section": "requirements"}
            },
            {
                "text": "Configuration Steps: After installation, configure the Neo4j database connection and Qdrant vector store settings in the docker-compose.yml file.",
                "chunk_id": "install_guide_3",
                "chunk_index": 2,
                "source_file": "installation_guide.txt",
                "metadata": {"content_type": "procedural", "section": "configuration"}
            },
            {
                "text": "A Christmas Carol by Charles Dickens: Marley was dead, to begin with. There is no doubt whatever about that. The register of his burial was signed by the clergyman, the clerk, the undertaker, and the chief mourner.",
                "chunk_id": "christmas_carol_1",
                "chunk_index": 0,
                "source_file": "a_christmas_carol.txt",
                "metadata": {"content_type": "narrative", "section": "opening"}
            },
            {
                "text": "Scrooge and Marley: Scrooge never painted out Old Marley's name. There it stood, years afterwards, above the warehouse door: Scrooge and Marley.",
                "chunk_id": "christmas_carol_2",
                "chunk_index": 1,
                "source_file": "a_christmas_carol.txt",
                "metadata": {"content_type": "narrative", "section": "character_introduction"}
            }
        ]
        
        # Add chunks to the retriever
        print(f"\nAdding {len(test_chunks)} test chunks to the retriever...")
        retriever.add_document_chunks(test_chunks)
        print("✅ Chunks added successfully")
        
        # Test retrieval with different query types
        test_queries = [
            {
                "query": "How do I install GraphRAG?",
                "expected_type": "technical",
                "description": "Technical installation query"
            },
            {
                "query": "What are the system requirements?",
                "expected_type": "technical", 
                "description": "Technical requirements query"
            },
            {
                "query": "Who is Marley in the story?",
                "expected_type": "narrative",
                "description": "Narrative character query"
            },
            {
                "query": "What happens at the beginning of A Christmas Carol?",
                "expected_type": "narrative",
                "description": "Narrative plot query"
            }
        ]
        
        print(f"\nTesting retrieval with {len(test_queries)} different query types...")
        
        for i, test_case in enumerate(test_queries, 1):
            print(f"\n--- Test {i}: {test_case['description']} ---")
            print(f"Query: '{test_case['query']}'")
            
            # Perform retrieval
            results = retriever.retrieve(test_case['query'], top_k=3)
            
            if results:
                print(f"✅ Retrieved {len(results)} results:")
                for j, result in enumerate(results[:2], 1):  # Show top 2 results
                    print(f"   {j}. Score: {result.score:.3f}")
                    print(f"      Source: {result.source}")
                    print(f"      Content: {result.content[:100]}...")
                    
                    # Check if metadata contains contextual information
                    if hasattr(result, 'metadata') and result.metadata:
                        metadata = result.metadata
                        if 'document_context' in metadata:
                            doc_context = metadata['document_context']
                            print(f"      Document type: {doc_context.get('document_type', 'unknown')}")
                            print(f"      Domain: {doc_context.get('domain', 'unknown')}")
                        
                        if 'chunk_context' in metadata:
                            chunk_context = metadata['chunk_context']
                            print(f"      Content type: {chunk_context.get('content_type', 'unknown')}")
                            print(f"      Position: {chunk_context.get('chunk_position', 'unknown')}")
            else:
                print("❌ No results retrieved")
        
        # Test vector search specifically
        print(f"\n--- Testing Vector Search ---")
        vector_results = retriever.vector_search("installation requirements", top_k=2)
        
        if vector_results:
            print(f"✅ Vector search returned {len(vector_results)} results:")
            for i, result in enumerate(vector_results, 1):
                print(f"   {i}. Score: {result.score:.3f}")
                print(f"      Source: {result.source}")
                print(f"      Content: {result.content[:80]}...")
        else:
            print("❌ Vector search returned no results")
        
        # Test document listing
        print(f"\n--- Testing Document Listing ---")
        documents = retriever.list_documents_in_vector_store()
        if documents:
            print(f"✅ Found {len(documents)} documents in vector store:")
            for doc in documents:
                print(f"   - {doc.get('document_name', 'unknown')}: {doc.get('chunk_count', 0)} chunks")
        else:
            print("❌ No documents found in vector store")
        
        print("\n✅ Contextual embeddings integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

def test_contextual_embeddings_performance():
    """Test performance improvements with contextual embeddings."""
    print("\nTesting contextual embeddings performance...")
    
    try:
        retriever = HybridRetriever()
        
        # Create a larger test dataset
        large_test_chunks = []
        for i in range(20):
            chunk = {
                "text": f"Technical documentation section {i+1}: This section describes the configuration and setup procedures for component {i+1}. The component requires specific parameters and follows established protocols.",
                "chunk_id": f"tech_chunk_{i+1}",
                "chunk_index": i,
                "source_file": "technical_documentation.txt",
                "metadata": {"content_type": "technical", "section": f"section_{i+1}"}
            }
            large_test_chunks.append(chunk)
        
        # Add chunks and measure time
        import time
        start_time = time.time()
        retriever.add_document_chunks(large_test_chunks)
        add_time = time.time() - start_time
        
        print(f"✅ Added {len(large_test_chunks)} chunks in {add_time:.2f} seconds")
        
        # Test retrieval performance
        start_time = time.time()
        results = retriever.retrieve("configuration setup procedures", top_k=5)
        retrieval_time = time.time() - start_time
        
        print(f"✅ Retrieved {len(results)} results in {retrieval_time:.3f} seconds")
        
        if results:
            print(f"   Top result score: {results[0].score:.3f}")
            print(f"   Average score: {sum(r.score for r in results) / len(results):.3f}")
        
        print("✅ Performance test completed!")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")

def main():
    """Run integration tests."""
    print("🧪 Testing Contextual Embeddings Integration")
    print("=" * 60)
    
    test_contextual_embeddings_integration()
    test_contextual_embeddings_performance()
    
    print("\n" + "=" * 60)
    print("✅ All integration tests completed!")

if __name__ == "__main__":
    main() 