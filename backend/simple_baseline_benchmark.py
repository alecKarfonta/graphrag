#!/usr/bin/env python3
"""
Simple baseline benchmark to compare with contextual enhancement results
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gutenqa_evaluator import GutenQAEvaluator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_baseline_evaluation():
    """Run simple baseline evaluation using Contriever"""
    logger.info("🚀 Starting Baseline Evaluation")
    start_time = time.time()
    
    # Initialize evaluator
    evaluator = GutenQAEvaluator()
    
    # Load dataset
    logger.info("📊 Loading GutenQA dataset...")
    success = evaluator.load_gutenqa_dataset()
    if not success:
        logger.error("❌ Failed to load dataset")
        return
    
    # Get stats
    stats = evaluator.get_dataset_statistics()
    logger.info(f"📊 Dataset loaded: {stats.get('total_books', 0)} books, {stats.get('total_questions', 0)} questions")
    
    # Run baseline evaluation on Christmas Carol
    test_book = "A_Christmas_Carol_-_Charles_Dickens"
    logger.info(f"📖 Running baseline evaluation on: {test_book}")
    
    try:
        result = evaluator.evaluate_baseline_retrieval(test_book, max_questions=30)
        
        # Print results
        print("\n" + "="*60)
        print("BASELINE EVALUATION RESULTS")
        print("="*60)
        print(f"📖 Test Book: {test_book}")
        print(f"📊 Total Questions: {result.total_questions}")
        print(f"✅ Correct Retrievals: {result.correct_retrievals}")
        print(f"🎯 Accuracy: {result.correct_retrievals / result.total_questions:.3f} ({result.correct_retrievals / result.total_questions * 100:.1f}%)")
        print(f"📈 DCG@1: {result.dcg_at_1:.3f}")
        print(f"📈 DCG@2: {result.dcg_at_2:.3f}")
        print(f"📈 DCG@5: {result.dcg_at_5:.3f}")
        print(f"📈 DCG@10: {result.dcg_at_10:.3f}")
        print(f"📈 DCG@20: {result.dcg_at_20:.3f}")
        print(f"⏱️  Execution Time: {time.time() - start_time:.2f} seconds")
        print("="*60)
        
        # Compare with contextual enhancement results
        print("\n" + "="*60)
        print("COMPARISON WITH CONTEXTUAL ENHANCEMENT")
        print("="*60)
        
        # These are the results from the previous run
        enhanced_accuracy = 0.7
        enhanced_dcg_at_1 = 0.7
        enhanced_dcg_at_5 = 0.756
        enhanced_dcg_at_10 = 0.779
        enhanced_correct = 21
        
        baseline_accuracy = result.correct_retrievals / result.total_questions
        
        print(f"📊 ACCURACY COMPARISON:")
        print(f"   Baseline (Contriever): {baseline_accuracy:.3f} ({baseline_accuracy*100:.1f}%)")
        print(f"   Enhanced (Contextual): {enhanced_accuracy:.3f} ({enhanced_accuracy*100:.1f}%)")
        print(f"   Improvement: {(enhanced_accuracy - baseline_accuracy):.3f} ({(enhanced_accuracy - baseline_accuracy)*100:+.1f}%)")
        
        print(f"\n📈 DCG@1 COMPARISON:")
        print(f"   Baseline: {result.dcg_at_1:.3f}")
        print(f"   Enhanced: {enhanced_dcg_at_1:.3f}")
        print(f"   Improvement: {(enhanced_dcg_at_1 - result.dcg_at_1):.3f} ({(enhanced_dcg_at_1 - result.dcg_at_1)/result.dcg_at_1*100:+.1f}%)")
        
        print(f"\n📈 DCG@5 COMPARISON:")
        print(f"   Baseline: {result.dcg_at_5:.3f}")
        print(f"   Enhanced: {enhanced_dcg_at_5:.3f}")
        print(f"   Improvement: {(enhanced_dcg_at_5 - result.dcg_at_5):.3f} ({(enhanced_dcg_at_5 - result.dcg_at_5)/result.dcg_at_5*100:+.1f}%)")
        
        print(f"\n📈 DCG@10 COMPARISON:")
        print(f"   Baseline: {result.dcg_at_10:.3f}")
        print(f"   Enhanced: {enhanced_dcg_at_10:.3f}")
        print(f"   Improvement: {(enhanced_dcg_at_10 - result.dcg_at_10):.3f} ({(enhanced_dcg_at_10 - result.dcg_at_10)/result.dcg_at_10*100:+.1f}%)")
        
        print(f"\n🎯 RETRIEVAL IMPROVEMENTS:")
        print(f"   Baseline Correct: {result.correct_retrievals}")
        print(f"   Enhanced Correct: {enhanced_correct}")
        print(f"   Additional Correct: {enhanced_correct - result.correct_retrievals}")
        
        print("="*60)
        
        logger.info("✅ Baseline evaluation completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Baseline evaluation failed: {e}")

if __name__ == "__main__":
    run_baseline_evaluation() 