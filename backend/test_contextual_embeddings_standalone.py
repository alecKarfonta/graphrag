"""
Standalone test for contextual embeddings without external dependencies.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from contextual_embeddings import ContextualEmbedder
import numpy as np

def test_contextual_embeddings_standalone():
    """Test contextual embeddings without external dependencies."""
    print("Testing contextual embeddings standalone functionality...")
    
    try:
        # Initialize embedder
        embedder = ContextualEmbedder()
        print("✅ Contextual embedder initialized")
        
        # Test with A Christmas Carol chunks (from the improvement plan)
        christmas_carol_chunks = [
            {
                "text": "Marley was dead, to begin with. There is no doubt whatever about that. The register of his burial was signed by the clergyman, the clerk, the undertaker, and the chief mourner.",
                "chunk_id": "christmas_carol_1",
                "chunk_index": 0,
                "source_file": "a_christmas_carol.txt",
                "metadata": {"content_type": "narrative", "section": "opening"}
            },
            {
                "text": "Scrooge never painted out Old Marley's name. There it stood, years afterwards, above the warehouse door: Scrooge and Marley.",
                "chunk_id": "christmas_carol_2",
                "chunk_index": 1,
                "source_file": "a_christmas_carol.txt",
                "metadata": {"content_type": "narrative", "section": "character_introduction"}
            },
            {
                "text": "The mention of Marley's funeral brings me back to the point I started from. There is no doubt that Marley was dead. This must be distinctly understood, or nothing wonderful can come of the story I am going to relate.",
                "chunk_id": "christmas_carol_3",
                "chunk_index": 2,
                "source_file": "a_christmas_carol.txt",
                "metadata": {"content_type": "narrative", "section": "narrative_setup"}
            }
        ]
        
        # Generate contextual embeddings
        print(f"\nGenerating contextual embeddings for {len(christmas_carol_chunks)} chunks...")
        contextual_embeddings = embedder.embed_document_chunks(
            christmas_carol_chunks, 
            "a_christmas_carol.txt",
            {"title": "A Christmas Carol", "author": "Charles Dickens", "genre": "novella"}
        )
        
        print(f"✅ Generated {len(contextual_embeddings)} contextual embeddings")
        
        # Analyze the embeddings
        for i, embedding in enumerate(contextual_embeddings):
            print(f"\n--- Chunk {i+1} Analysis ---")
            print(f"Original text: {embedding.original_text[:100]}...")
            print(f"Enhanced text length: {len(embedding.enhanced_text)}")
            print(f"Document type: {embedding.document_context.document_type}")
            print(f"Domain: {embedding.document_context.domain}")
            print(f"Technical level: {embedding.document_context.technical_level}")
            print(f"Content type: {embedding.chunk_context.content_type}")
            print(f"Chunk position: {embedding.chunk_context.chunk_position}")
            print(f"Key entities: {embedding.chunk_context.key_entities}")
            print(f"Importance score: {embedding.chunk_context.importance_score:.2f}")
            
            # Show enhanced text snippet
            enhanced_snippet = embedding.enhanced_text[:300] + "..." if len(embedding.enhanced_text) > 300 else embedding.enhanced_text
            print(f"Enhanced text snippet: {enhanced_snippet}")
        
        # Test similarity between related chunks
        print(f"\n--- Testing Semantic Similarity ---")
        if len(contextual_embeddings) >= 2:
            # Compare first two chunks (both about Marley)
            emb1 = contextual_embeddings[0].embedding
            emb2 = contextual_embeddings[1].embedding
            
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            print(f"Similarity between Marley-related chunks: {similarity:.3f}")
            
            if similarity > 0.7:
                print("✅ High similarity detected between related chunks")
            else:
                print("⚠️ Lower than expected similarity")
        
        # Test with technical document for comparison
        print(f"\n--- Testing Technical Document ---")
        technical_chunks = [
            {
                "text": "Installation Procedure: Download the GraphRAG package and extract it to your desired directory. Run the setup script with administrator privileges.",
                "chunk_id": "tech_1",
                "chunk_index": 0,
                "source_file": "installation_guide.txt",
                "metadata": {"content_type": "procedural"}
            }
        ]
        
        tech_embeddings = embedder.embed_document_chunks(
            technical_chunks,
            "installation_guide.txt",
            {"title": "GraphRAG Installation Guide", "type": "technical_manual"}
        )
        
        if tech_embeddings:
            tech_embedding = tech_embeddings[0]
            print(f"✅ Technical document embedding generated:")
            print(f"   Document type: {tech_embedding.document_context.document_type}")
            print(f"   Domain: {tech_embedding.document_context.domain}")
            print(f"   Technical level: {tech_embedding.document_context.technical_level}")
            print(f"   Content type: {tech_embedding.chunk_context.content_type}")
            
            # Compare with narrative document
            if contextual_embeddings:
                narrative_emb = contextual_embeddings[0].embedding
                tech_emb = tech_embedding.embedding
                
                cross_similarity = np.dot(narrative_emb, tech_emb) / (np.linalg.norm(narrative_emb) * np.linalg.norm(tech_emb))
                print(f"   Cross-document similarity (narrative vs technical): {cross_similarity:.3f}")
                
                if cross_similarity < 0.5:
                    print("✅ Low similarity between different document types (good separation)")
                else:
                    print("⚠️ Higher than expected similarity between different document types")
        
        # Test cache functionality
        print(f"\n--- Testing Cache Functionality ---")
        cache_size_before = embedder.get_cache_size()
        print(f"Cache size before: {cache_size_before}")
        
        # Generate embeddings again (should use cache)
        cached_embeddings = embedder.embed_document_chunks(
            christmas_carol_chunks, 
            "a_christmas_carol.txt"
        )
        
        cache_size_after = embedder.get_cache_size()
        print(f"Cache size after: {cache_size_after}")
        
        if cache_size_after[1] > cache_size_before[1]:  # Document contexts cached
            print("✅ Document context caching working")
        else:
            print("⚠️ Document context caching may not be working")
        
        print("\n✅ Standalone contextual embeddings test completed successfully!")
        
    except Exception as e:
        print(f"❌ Standalone test failed: {e}")
        import traceback
        traceback.print_exc()

def test_contextual_enhancement_quality():
    """Test the quality of contextual enhancement."""
    print("\nTesting contextual enhancement quality...")
    
    try:
        embedder = ContextualEmbedder()
        
        # Test with different document types to see enhancement quality
        test_cases = [
            {
                "name": "Research Paper",
                "chunks": [
                    {
                        "text": "The methodology employed a mixed-methods approach combining quantitative analysis with qualitative interviews. Statistical significance was tested using p < 0.05.",
                        "chunk_id": "research_1",
                        "chunk_index": 0,
                        "source_file": "research_paper.txt",
                        "metadata": {"content_type": "methodology"}
                    }
                ],
                "metadata": {"title": "Research Study", "type": "academic_paper"}
            },
            {
                "name": "Legal Document",
                "chunks": [
                    {
                        "text": "Section 1.1: Definitions. For the purposes of this agreement, 'Party' shall mean any signatory to this contract. 'Effective Date' shall mean the date of execution.",
                        "chunk_id": "legal_1",
                        "chunk_index": 0,
                        "source_file": "legal_contract.txt",
                        "metadata": {"content_type": "definition"}
                    }
                ],
                "metadata": {"title": "Legal Contract", "type": "legal_document"}
            }
        ]
        
        for test_case in test_cases:
            print(f"\n--- Testing {test_case['name']} ---")
            
            embeddings = embedder.embed_document_chunks(
                test_case["chunks"],
                test_case["chunks"][0]["source_file"],
                test_case["metadata"]
            )
            
            if embeddings:
                embedding = embeddings[0]
                print(f"✅ {test_case['name']} enhancement:")
                print(f"   Document type: {embedding.document_context.document_type}")
                print(f"   Domain: {embedding.document_context.domain}")
                print(f"   Technical level: {embedding.document_context.technical_level}")
                print(f"   Content type: {embedding.chunk_context.content_type}")
                print(f"   Context parts: {embedding.embedding_metadata['context_parts']}")
                
                # Show enhancement ratio
                enhancement_ratio = len(embedding.enhanced_text) / len(embedding.original_text)
                print(f"   Enhancement ratio: {enhancement_ratio:.2f}x")
                
                if enhancement_ratio > 1.5:
                    print("   ✅ Significant contextual enhancement applied")
                else:
                    print("   ⚠️ Minimal contextual enhancement")
        
        print("\n✅ Contextual enhancement quality test completed!")
        
    except Exception as e:
        print(f"❌ Enhancement quality test failed: {e}")

def main():
    """Run standalone tests."""
    print("🧪 Testing Contextual Embeddings Standalone")
    print("=" * 50)
    
    test_contextual_embeddings_standalone()
    test_contextual_enhancement_quality()
    
    print("\n" + "=" * 50)
    print("✅ All standalone tests completed!")

if __name__ == "__main__":
    main() 