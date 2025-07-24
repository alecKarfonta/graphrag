"""
Test script for contextual embeddings implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from contextual_embeddings import ContextualEmbedder, DocumentContext, ChunkContext
import numpy as np

def test_contextual_embedder_initialization():
    """Test that the contextual embedder initializes correctly."""
    print("Testing contextual embedder initialization...")
    
    try:
        embedder = ContextualEmbedder(
            model_name="all-MiniLM-L6-v2",
            context_window_size=200,
            max_context_length=512
        )
        print("✅ Contextual embedder initialized successfully")
        return embedder
    except Exception as e:
        print(f"❌ Failed to initialize contextual embedder: {e}")
        return None

def test_document_context_creation():
    """Test document context creation."""
    print("\nTesting document context creation...")
    
    embedder = test_contextual_embedder_initialization()
    if not embedder:
        return
    
    # Test chunks for a technical document
    technical_chunks = [
        {
            "text": "Installation Procedure: This guide provides step-by-step instructions for installing the software system. The installation process requires administrative privileges and approximately 500MB of disk space.",
            "chunk_id": "tech_chunk_1",
            "chunk_index": 0,
            "source_file": "technical_manual.txt",
            "metadata": {"content_type": "procedural"}
        },
        {
            "text": "System Requirements: The software requires Windows 10 or later, 4GB RAM minimum, and 1GB free disk space. Network connectivity is required for license validation.",
            "chunk_id": "tech_chunk_2", 
            "chunk_index": 1,
            "source_file": "technical_manual.txt",
            "metadata": {"content_type": "specification"}
        },
        {
            "text": "Configuration Steps: After installation, configure the database connection parameters in the config.ini file. Set the server address, port number, and authentication credentials.",
            "chunk_id": "tech_chunk_3",
            "chunk_index": 2,
            "source_file": "technical_manual.txt",
            "metadata": {"content_type": "procedural"}
        }
    ]
    
    # Create document context
    doc_context = embedder.create_document_context(
        "technical_manual.txt", 
        technical_chunks,
        {"title": "Software Installation Guide", "author": "Technical Team"}
    )
    
    print(f"✅ Document context created:")
    print(f"   - Document type: {doc_context.document_type}")
    print(f"   - Domain: {doc_context.domain}")
    print(f"   - Technical level: {doc_context.technical_level}")
    print(f"   - Main topics: {doc_context.main_topics}")
    print(f"   - Summary: {doc_context.document_summary[:100]}...")

def test_chunk_context_creation():
    """Test chunk context creation."""
    print("\nTesting chunk context creation...")
    
    embedder = test_contextual_embedder_initialization()
    if not embedder:
        return
    
    # Test chunks
    chunks = [
        {
            "text": "Chapter 1: Introduction. This chapter provides an overview of the main concepts and principles discussed in this book.",
            "chunk_id": "chapter_1",
            "chunk_index": 0,
            "source_file": "book.txt",
            "metadata": {"content_type": "introduction"}
        },
        {
            "text": "The protagonist, John Smith, enters the room with a sense of trepidation. His footsteps echo through the empty hallway as he approaches the mysterious door.",
            "chunk_id": "chapter_2", 
            "chunk_index": 1,
            "source_file": "book.txt",
            "metadata": {"content_type": "narrative"}
        },
        {
            "text": "In conclusion, the findings demonstrate significant improvements in performance metrics across all test scenarios.",
            "chunk_id": "chapter_3",
            "chunk_index": 2,
            "source_file": "book.txt", 
            "metadata": {"content_type": "conclusion"}
        }
    ]
    
    # Create document context
    doc_context = embedder.create_document_context("book.txt", chunks)
    
    # Create chunk context for middle chunk
    chunk_context = embedder.create_chunk_context(
        chunks[1], 1, chunks, doc_context
    )
    
    print(f"✅ Chunk context created:")
    print(f"   - Content type: {chunk_context.content_type}")
    print(f"   - Position: {chunk_context.chunk_position}")
    print(f"   - Key entities: {chunk_context.key_entities}")
    print(f"   - Importance score: {chunk_context.importance_score:.2f}")

def test_contextual_embedding_generation():
    """Test contextual embedding generation."""
    print("\nTesting contextual embedding generation...")
    
    embedder = test_contextual_embedder_initialization()
    if not embedder:
        return
    
    # Test chunks for different document types
    test_cases = [
        {
            "name": "Technical Document",
            "chunks": [
                {
                    "text": "API Configuration: Set the authentication token in the header. Use Bearer token format for secure access.",
                    "chunk_id": "api_config",
                    "chunk_index": 0,
                    "source_file": "api_docs.txt",
                    "metadata": {"content_type": "technical"}
                }
            ]
        },
        {
            "name": "Narrative Document", 
            "chunks": [
                {
                    "text": "The old man sat by the window, watching the rain fall gently on the cobblestone streets below.",
                    "chunk_id": "narrative_1",
                    "chunk_index": 0,
                    "source_file": "story.txt",
                    "metadata": {"content_type": "narrative"}
                }
            ]
        },
        {
            "name": "Academic Document",
            "chunks": [
                {
                    "text": "The research methodology employed a mixed-methods approach combining quantitative analysis with qualitative interviews.",
                    "chunk_id": "methodology",
                    "chunk_index": 0,
                    "source_file": "research_paper.txt",
                    "metadata": {"content_type": "academic"}
                }
            ]
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['name']} ---")
        
        # Generate contextual embeddings
        contextual_embeddings = embedder.embed_document_chunks(
            test_case["chunks"], 
            test_case["chunks"][0]["source_file"]
        )
        
        if contextual_embeddings:
            embedding = contextual_embeddings[0]
            print(f"✅ Generated contextual embedding:")
            print(f"   - Original text length: {len(embedding.original_text)}")
            print(f"   - Enhanced text length: {len(embedding.enhanced_text)}")
            print(f"   - Embedding dimension: {len(embedding.embedding)}")
            print(f"   - Document type: {embedding.document_context.document_type}")
            print(f"   - Content type: {embedding.chunk_context.content_type}")
            print(f"   - Context parts: {embedding.embedding_metadata['context_parts']}")
            
            # Show a snippet of enhanced text
            enhanced_snippet = embedding.enhanced_text[:200] + "..." if len(embedding.enhanced_text) > 200 else embedding.enhanced_text
            print(f"   - Enhanced text snippet: {enhanced_snippet}")
        else:
            print(f"❌ Failed to generate contextual embedding for {test_case['name']}")

def test_embedding_similarity():
    """Test that contextual embeddings capture semantic similarity correctly."""
    print("\nTesting embedding similarity...")
    
    embedder = test_contextual_embedder_initialization()
    if not embedder:
        return
    
    # Create similar chunks
    similar_chunks = [
        {
            "text": "Install the software by running the setup.exe file. Follow the installation wizard prompts.",
            "chunk_id": "install_1",
            "chunk_index": 0,
            "source_file": "install_guide.txt"
        },
        {
            "text": "To install the application, execute the installer and complete the setup process step by step.",
            "chunk_id": "install_2", 
            "chunk_index": 0,
            "source_file": "install_guide.txt"
        }
    ]
    
    # Create different chunks
    different_chunks = [
        {
            "text": "The character development in this novel explores themes of redemption and personal growth.",
            "chunk_id": "literary_1",
            "chunk_index": 0,
            "source_file": "literary_analysis.txt"
        }
    ]
    
    # Generate embeddings
    similar_embeddings = embedder.embed_document_chunks(similar_chunks, "install_guide.txt")
    different_embeddings = embedder.embed_document_chunks(different_chunks, "literary_analysis.txt")
    
    if similar_embeddings and different_embeddings:
        # Calculate similarities
        similar_sim = np.dot(similar_embeddings[0].embedding, similar_embeddings[1].embedding) / (
            np.linalg.norm(similar_embeddings[0].embedding) * np.linalg.norm(similar_embeddings[1].embedding)
        )
        
        different_sim = np.dot(similar_embeddings[0].embedding, different_embeddings[0].embedding) / (
            np.linalg.norm(similar_embeddings[0].embedding) * np.linalg.norm(different_embeddings[0].embedding)
        )
        
        print(f"✅ Similarity scores:")
        print(f"   - Similar chunks: {similar_sim:.3f}")
        print(f"   - Different chunks: {different_sim:.3f}")
        print(f"   - Similarity difference: {similar_sim - different_sim:.3f}")
        
        if similar_sim > different_sim:
            print("✅ Contextual embeddings correctly capture semantic similarity")
        else:
            print("⚠️ Similarity scores may need adjustment")

def test_cache_functionality():
    """Test caching functionality."""
    print("\nTesting cache functionality...")
    
    embedder = test_contextual_embedder_initialization()
    if not embedder:
        return
    
    # Test chunks
    chunks = [
        {
            "text": "Test chunk for caching functionality.",
            "chunk_id": "cache_test",
            "chunk_index": 0,
            "source_file": "cache_test.txt"
        }
    ]
    
    # Generate embeddings twice
    embeddings1 = embedder.embed_document_chunks(chunks, "cache_test.txt")
    embeddings2 = embedder.embed_document_chunks(chunks, "cache_test.txt")
    
    if embeddings1 and embeddings2:
        # Check if embeddings are identical (cached)
        are_identical = np.array_equal(embeddings1[0].embedding, embeddings2[0].embedding)
        print(f"✅ Cached embeddings are identical: {are_identical}")
        
        # Check cache size
        cache_size = embedder.get_cache_size()
        print(f"✅ Cache sizes - Embeddings: {cache_size[0]}, Document contexts: {cache_size[1]}")
        
        # Test cache clearing
        embedder.clear_cache()
        new_cache_size = embedder.get_cache_size()
        print(f"✅ After clearing - Embeddings: {new_cache_size[0]}, Document contexts: {new_cache_size[1]}")

def main():
    """Run all tests."""
    print("🧪 Testing Contextual Embeddings Implementation")
    print("=" * 50)
    
    # Run tests
    test_contextual_embedder_initialization()
    test_document_context_creation()
    test_chunk_context_creation()
    test_contextual_embedding_generation()
    test_embedding_similarity()
    test_cache_functionality()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 