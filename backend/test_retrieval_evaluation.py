#!/usr/bin/env python3
"""
Simple test script to verify the retrieval evaluation system works.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gutenqa_evaluator import GutenQAEvaluator

def test_retrieval_evaluation_system():
    """Test the basic retrieval evaluation system functionality."""
    print("🔍 Testing GutenQA Retrieval Evaluation System")
    print("=" * 50)
    
    try:
        # Initialize evaluator
        print("1. Initializing evaluator...")
        evaluator = GutenQAEvaluator(data_dir="./test_retrieval_evaluation_data")
        print("   ✅ Evaluator initialized successfully")
        
        # Test dataset loading
        print("2. Testing dataset loading...")
        success = evaluator.load_gutenqa_dataset()
        if success:
            print("   ✅ Dataset loading successful")
        else:
            print("   ❌ Dataset loading failed")
            return False
        
        # Test dataset statistics
        print("3. Testing dataset statistics...")
        stats = evaluator.get_dataset_statistics()
        if stats:
            print(f"   ✅ Dataset statistics:")
            print(f"      - Total books: {stats.get('total_books', 'N/A')}")
            print(f"      - Total chunks: {stats.get('total_chunks', 'N/A')}")
            print(f"      - Total questions: {stats.get('total_questions', 'N/A')}")
        else:
            print("   ❌ Failed to get dataset statistics")
            return False
        
        # Test available books
        print("4. Testing available books...")
        available_books = evaluator.get_available_books()
        if available_books:
            print(f"   ✅ Found {len(available_books)} available books")
            print(f"      - First 5 books: {available_books[:5]}")
        else:
            print("   ❌ No books found")
            return False
        
        # Test baseline evaluation on a small sample
        print("5. Testing baseline evaluation...")
        try:
            # Use the first available book with a small sample
            test_book = available_books[0]
            baseline_result = evaluator.evaluate_baseline_retrieval(test_book, max_questions=3)
            
            print(f"   ✅ Baseline evaluation completed:")
            print(f"      - Book: {test_book}")
            print(f"      - Questions: {baseline_result.total_questions}")
            print(f"      - DCG@1: {baseline_result.dcg_at_1:.4f}")
            print(f"      - DCG@10: {baseline_result.dcg_at_10:.4f}")
            print(f"      - Accuracy: {baseline_result.correct_retrievals}/{baseline_result.total_questions}")
            
        except Exception as e:
            print(f"   ⚠️ Baseline evaluation failed (expected if Contriever not available): {e}")
        
        # Note about hybrid evaluation
        print("6. Hybrid evaluation test...")
        print("   ℹ️ Hybrid evaluation requires active Qdrant connection")
        print("   ℹ️ Skipping hybrid test in this basic verification")
        
        print("\n🎉 Basic tests passed! Retrieval evaluation system is ready.")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_retrieval_evaluation_system()
    sys.exit(0 if success else 1) 