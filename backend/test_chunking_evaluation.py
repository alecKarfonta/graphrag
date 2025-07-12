#!/usr/bin/env python3
"""
Simple test script to verify the chunking evaluation system works.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from wikisection_evaluator import WikiSectionEvaluator

def test_evaluation_system():
    """Test the basic evaluation system functionality."""
    print("🧪 Testing WikiSection Evaluation System")
    print("=" * 50)
    
    try:
        # Initialize evaluator
        print("1. Initializing evaluator...")
        evaluator = WikiSectionEvaluator(data_dir="./test_evaluation_data")
        print("   ✅ Evaluator initialized successfully")
        
        # Test dataset download
        print("2. Testing dataset download...")
        success = evaluator.download_dataset()
        if success:
            print("   ✅ Dataset download successful")
        else:
            print("   ❌ Dataset download failed")
            return False
        
        # Test data loading
        print("3. Testing data loading...")
        documents = evaluator.load_wikisection_data("en_disease")
        if documents:
            print(f"   ✅ Loaded {len(documents)} documents from en_disease subset")
        else:
            print("   ❌ Failed to load documents")
            return False
        
        # Test evaluation on small sample
        print("4. Testing evaluation on small sample...")
        small_sample = documents[:5]  # Use just 5 documents for quick test
        result = evaluator.evaluate_chunking(small_sample)
        
        print(f"   ✅ Evaluation completed:")
        print(f"      - Precision: {result.precision:.4f}")
        print(f"      - Recall: {result.recall:.4f}")
        print(f"      - F1-Score: {result.f1_score:.4f}")
        print(f"      - Boundaries: {result.correct_boundaries}/{result.total_boundaries}")
        
        # Test baseline comparison
        print("5. Testing baseline comparison...")
        comparison = evaluator.compare_with_baseline(small_sample[:3], baseline_chunk_size=300)
        
        semantic_f1 = comparison["semantic"].f1_score
        baseline_f1 = comparison["baseline"].f1_score
        
        print(f"   ✅ Baseline comparison completed:")
        print(f"      - Semantic F1: {semantic_f1:.4f}")
        print(f"      - Baseline F1: {baseline_f1:.4f}")
        print(f"      - Improvement: {semantic_f1 - baseline_f1:.4f}")
        
        print("\n🎉 All tests passed! Evaluation system is working correctly.")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_evaluation_system()
    sys.exit(0 if success else 1) 