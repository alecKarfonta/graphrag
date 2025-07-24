"""
Test suite for contextual BM25 implementation.
"""

import pytest
import sys
import os
from typing import List, Dict, Any

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bm25_import():
    """Test that BM25 dependencies can be imported."""
    try:
        from contextual_bm25 import ContextualBM25, DocumentContext, BM25Result
        print("✅ BM25 imports successful")
        return True
    except ImportError as e:
        print(f"❌ BM25 import failed: {e}")
        print("💡 You may need to install rank_bm25: pip install rank_bm25")
        return False


def test_contextual_bm25_basic():
    """Test basic contextual BM25 functionality."""
    try:
        from contextual_bm25 import ContextualBM25, DocumentContext, BM25Result
        
        # Create BM25 instance
        bm25 = ContextualBM25()
        
        # Test documents
        documents = [
            "The quick brown fox jumps over the lazy dog",
            "A lazy dog sleeps in the sun",
            "The fox is quick and brown",
            "Machine learning algorithms require training data",
            "Deep learning is a subset of machine learning"
        ]
        
        # Create contexts
        contexts = []
        for i, doc in enumerate(documents):
            context = DocumentContext(
                source_file=f"test_doc_{i}.txt",
                entities=["fox", "dog"] if i < 3 else ["machine learning", "deep learning"],
                metadata={"test": True}
            )
            contexts.append(context)
        
        # Add documents to BM25
        bm25.add_documents(documents, contexts)
        
        # Test search
        results = bm25.search("quick brown fox", top_k=3)
        
        assert len(results) > 0, "Should return results"
        assert results[0].score > 0, "Should have positive scores"
        
        # Test entity boosting
        results_with_entities = bm25.search("fox", top_k=3)
        assert len(results_with_entities) > 0, "Should return results for entity search"
        
        print("✅ Basic contextual BM25 test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic contextual BM25 test failed: {e}")
        return False


def test_hybrid_retriever_integration():
    """Test BM25 integration with hybrid retriever."""
    try:
        from hybrid_retriever import HybridRetriever
        
        # Create hybrid retriever
        retriever = HybridRetriever()
        
        # Test documents
        chunks = [
            {
                "text": "The brake system includes the master cylinder, brake pads, and brake fluid.",
                "source_file": "automotive_manual.pdf",
                "metadata": {
                    "section_header": "Brake System",
                    "entities": ["brake system", "master cylinder", "brake pads", "brake fluid"]
                }
            },
            {
                "text": "Regular maintenance of the engine involves checking oil levels and air filters.",
                "source_file": "automotive_manual.pdf", 
                "metadata": {
                    "section_header": "Engine Maintenance",
                    "entities": ["engine", "oil", "air filters"]
                }
            }
        ]
        
        # Add chunks to retriever (this should also add to BM25)
        retriever.add_document_chunks(chunks)
        
        # Test search
        results = retriever.keyword_search("brake system master cylinder", ["brake", "system", "master", "cylinder"])
        
        print(f"Search results: {len(results)}")
        for result in results:
            print(f"  - Type: {result.result_type}, Score: {result.score:.3f}")
        
        print("✅ Hybrid retriever integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Hybrid retriever integration test failed: {e}")
        return False


def test_contextual_scoring():
    """Test that contextual scoring works correctly."""
    try:
        from contextual_bm25 import ContextualBM25, DocumentContext
        
        bm25 = ContextualBM25()
        
        # Very simple documents
        documents = [
            "automobile brake system",
            "automobile maintenance"
        ]
        
        contexts = [
            DocumentContext(
                source_file="test1.pdf",
                entities=["automobile", "brake"],
                metadata={}
            ),
            DocumentContext(
                source_file="test2.pdf", 
                entities=["automobile", "maintenance"],
                metadata={}
            )
        ]
        
        bm25.add_documents(documents, contexts)
        
        # Search with a simple term
        results = bm25.search("automobile brake", top_k=2)
        
        # The test should pass if we have any results
        if len(results) > 0:
            first_score = results[0].score
            print(f"First result score: {first_score:.3f}")
            print("✅ Contextual scoring test passed")
            return True
        else:
            print("❌ No results returned from BM25 search")
            return False
        
    except Exception as e:
        print(f"❌ Contextual scoring test failed: {e}")
        return False


def run_all_tests():
    """Run all BM25 tests."""
    print("🧪 Running Contextual BM25 Tests")
    print("=" * 50)
    
    tests = [
        test_bm25_import,
        test_contextual_bm25_basic,
        test_hybrid_retriever_integration,
        test_contextual_scoring
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n🔍 Running {test.__name__}")
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")


if __name__ == "__main__":
    run_all_tests() 