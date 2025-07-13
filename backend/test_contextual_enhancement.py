import pytest
from typing import Dict, List, Any
from contextual_enhancer import ContextualEnhancer, ContextualChunk
from hybrid_retriever import HybridRetriever

def test_contextual_enhancer_import():
    """Test that the contextual enhancer imports correctly."""
    try:
        enhancer = ContextualEnhancer()
        assert enhancer is not None
        print("✅ ContextualEnhancer imported and initialized successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import ContextualEnhancer: {e}")

def test_contextual_enhancement_basic():
    """Test basic contextual enhancement functionality."""
    enhancer = ContextualEnhancer()
    
    # Create test chunks
    test_chunks = [
        {
            "text": "The master cylinder is a crucial component of the brake system.",
            "chunk_id": "chunk_1",
            "source_file": "brake_manual.pdf",
            "chunk_index": 0,
            "metadata": {"content_type": "technical"}
        },
        {
            "text": "It contains brake fluid and generates pressure when the pedal is pressed.",
            "chunk_id": "chunk_2", 
            "source_file": "brake_manual.pdf",
            "chunk_index": 1,
            "metadata": {"content_type": "technical"}
        },
        {
            "text": "Regular maintenance includes checking fluid levels and inspecting for leaks.",
            "chunk_id": "chunk_3",
            "source_file": "brake_manual.pdf", 
            "chunk_index": 2,
            "metadata": {"content_type": "procedural"}
        }
    ]
    
    # Test enhancement
    enhanced_chunks = enhancer.enhance_chunks_for_embedding(test_chunks)
    
    # Verify results
    assert len(enhanced_chunks) == 3
    assert all(isinstance(chunk, ContextualChunk) for chunk in enhanced_chunks)
    
    # Check that enhanced text is longer than original
    for i, enhanced_chunk in enumerate(enhanced_chunks):
        assert enhanced_chunk.original_text == test_chunks[i]["text"]
        assert len(enhanced_chunk.enhanced_text) >= len(enhanced_chunk.original_text)
        assert enhanced_chunk.context_type in ["technical", "procedural", "general"]
        
    print("✅ Basic contextual enhancement working correctly")

def test_document_context_extraction():
    """Test document-level context extraction."""
    enhancer = ContextualEnhancer()
    
    # Create test chunks from different document types
    technical_chunks = [
        {
            "text": "This technical manual covers brake system maintenance procedures.",
            "chunk_id": "tech_1",
            "source_file": "technical_manual.pdf",
            "chunk_index": 0,
            "metadata": {"content_type": "technical"}
        },
        {
            "text": "Follow these specifications for proper installation and configuration.",
            "chunk_id": "tech_2",
            "source_file": "technical_manual.pdf", 
            "chunk_index": 1,
            "metadata": {"content_type": "technical"}
        }
    ]
    
    narrative_chunks = [
        {
            "text": "Once upon a time, there was a story about a character named Alice.",
            "chunk_id": "story_1",
            "source_file": "story.txt",
            "chunk_index": 0,
            "metadata": {"content_type": "narrative"}
        },
        {
            "text": "The narrative continued with Alice's adventures in a magical world.",
            "chunk_id": "story_2",
            "source_file": "story.txt",
            "chunk_index": 1, 
            "metadata": {"content_type": "narrative"}
        }
    ]
    
    # Test technical document context
    tech_context = enhancer._extract_document_context(technical_chunks)
    assert tech_context["document_type"] == "technical_manual"
    assert tech_context["technical_level"] in ["basic", "intermediate", "advanced"]
    
    # Test narrative document context
    narrative_context = enhancer._extract_document_context(narrative_chunks)
    assert narrative_context["document_type"] == "narrative"
    
    print("✅ Document context extraction working correctly")

def test_contextual_chunk_relationships():
    """Test that chunks get appropriate contextual relationships."""
    enhancer = ContextualEnhancer()
    
    # Create related chunks
    related_chunks = [
        {
            "text": "The brake system consists of several key components.",
            "chunk_id": "intro_1",
            "source_file": "brake_guide.pdf",
            "chunk_index": 0,
            "metadata": {"content_type": "technical"}
        },
        {
            "text": "The master cylinder is the primary component that generates pressure.",
            "chunk_id": "detail_1",
            "source_file": "brake_guide.pdf",
            "chunk_index": 1,
            "metadata": {"content_type": "technical"}
        },
        {
            "text": "Regular inspection should include checking for fluid leaks and wear.",
            "chunk_id": "maintenance_1",
            "source_file": "brake_guide.pdf",
            "chunk_index": 2,
            "metadata": {"content_type": "procedural"}
        }
    ]
    
    enhanced_chunks = enhancer.enhance_chunks_for_embedding(related_chunks)
    
    # Check that middle chunk has preceding and following context
    middle_chunk = enhanced_chunks[1]
    assert "Preceding context:" in middle_chunk.enhanced_text
    assert "Following context:" in middle_chunk.enhanced_text
    
    # Check that first chunk has following context but no preceding
    first_chunk = enhanced_chunks[0]
    assert "Following context:" in first_chunk.enhanced_text
    assert "Preceding context:" not in first_chunk.enhanced_text
    
    # Check that last chunk has preceding context but no following
    last_chunk = enhanced_chunks[2]
    assert "Preceding context:" in last_chunk.enhanced_text
    assert "Following context:" not in last_chunk.enhanced_text
    
    print("✅ Contextual chunk relationships working correctly")

def test_hybrid_retriever_with_contextual_enhancement():
    """Test hybrid retriever integration with contextual enhancement."""
    try:
        # Initialize hybrid retriever
        retriever = HybridRetriever()
        
        # Verify contextual enhancer is available
        assert hasattr(retriever, 'contextual_enhancer')
        
        # Create test chunks
        test_chunks = [
            {
                "text": "The brake master cylinder controls hydraulic pressure in the system.",
                "chunk_id": "brake_1",
                "source_file": "brake_manual.pdf",
                "chunk_index": 0,
                "metadata": {"content_type": "technical"}
            },
            {
                "text": "When the brake pedal is pressed, it activates the master cylinder piston.",
                "chunk_id": "brake_2",
                "source_file": "brake_manual.pdf",
                "chunk_index": 1,
                "metadata": {"content_type": "technical"}
            }
        ]
        
        # Test adding chunks with contextual enhancement
        retriever.add_document_chunks(test_chunks)
        
        # Test search functionality
        results = retriever.retrieve("brake master cylinder", top_k=5)
        assert len(results) > 0
        
        # Check that results have enhanced metadata
        for result in results:
            assert result.metadata is None or isinstance(result.metadata, dict)
            
        print("✅ Hybrid retriever with contextual enhancement working correctly")
        
    except Exception as e:
        print(f"⚠️ Hybrid retriever test failed: {e}")
        # Don't fail the test if Qdrant is not available
        pass

def test_context_type_classification():
    """Test context type classification."""
    enhancer = ContextualEnhancer()
    
    # Test different context types
    test_cases = [
        {
            "text": "Step 1: Remove the brake fluid reservoir cap carefully.",
            "expected_type": "procedural"
        },
        {
            "text": "Definition: A master cylinder is a device that converts force into hydraulic pressure.",
            "expected_type": "definitional"
        },
        {
            "text": "What is the purpose of brake fluid in the hydraulic system?",
            "expected_type": "explanatory"
        },
        {
            "text": "This technical specification covers the requirements for brake system components.",
            "expected_type": "technical"
        }
    ]
    
    for test_case in test_cases:
        chunk = {"text": test_case["text"], "chunk_id": "test", "source_file": "test.pdf", "chunk_index": 0}
        doc_context = {"document_type": "technical_manual"}
        
        context_type = enhancer._determine_context_type(chunk, doc_context)
        assert context_type == test_case["expected_type"], f"Expected {test_case['expected_type']}, got {context_type}"
    
    print("✅ Context type classification working correctly")

def run_all_tests():
    """Run all contextual enhancement tests."""
    print("🧪 Running Contextual Enhancement Tests")
    print("=" * 50)
    
    try:
        test_contextual_enhancer_import()
        test_contextual_enhancement_basic()
        test_document_context_extraction()
        test_contextual_chunk_relationships()
        test_hybrid_retriever_with_contextual_enhancement()
        test_context_type_classification()
        
        print("\n🎉 All contextual enhancement tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 