#!/usr/bin/env python3
"""
Multi-book benchmark script to evaluate contextual enhancement across multiple books
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from statistics import mean, stdev

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gutenqa_evaluator import GutenQAEvaluator
from simple_baseline_benchmark import run_baseline_evaluation

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiBookBenchmark:
    """Benchmark contextual enhancement across multiple books"""
    
    def __init__(self):
        self.evaluator = GutenQAEvaluator()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'contextual_enhancement_available': True,
                'books_tested': [],
                'total_books': 0,
                'total_questions': 0
            },
            'book_results': {},
            'aggregated_results': {},
            'comparison_summary': {}
        }
        
    def run_multi_book_benchmark(self, 
                                books: Optional[List[str]] = None, 
                                max_books: int = 10,
                                questions_per_book: int = 30) -> Dict[str, Any]:
        """Run benchmark across multiple books"""
        
        logger.info(f"🚀 Starting multi-book benchmark")
        start_time = time.time()
        
        # Load dataset
        if not self.evaluator.load_gutenqa_dataset():
            logger.error("❌ Failed to load GutenQA dataset")
            return self.results
            
        # Get available books
        available_books = self.evaluator.get_available_books()
        logger.info(f"📚 Found {len(available_books)} available books")
        
        # Select books to test
        if books is None:
            # Use first N books for comprehensive testing
            books = available_books[:max_books]
        else:
            # Validate requested books
            books = [book for book in books if book in available_books]
            
        if not books:
            logger.error("❌ No valid books to test")
            return self.results
            
        logger.info(f"📖 Testing {len(books)} books with {questions_per_book} questions each")
        
        # Test each book
        enhanced_results = []
        baseline_results = []
        
        for i, book in enumerate(books):
            logger.info(f"📖 Testing book {i+1}/{len(books)}: {book}")
            
            # Test with contextual enhancement
            enhanced_result = self._test_book_enhanced(book, questions_per_book)
            if enhanced_result:
                enhanced_results.append(enhanced_result)
                
            # Test with baseline
            baseline_result = self._test_book_baseline(book, questions_per_book)
            if baseline_result:
                baseline_results.append(baseline_result)
                
            self.results['book_results'][book] = {
                'enhanced': enhanced_result,
                'baseline': baseline_result
            }
            
                         # Progress update
            enhanced_acc = enhanced_result.get('accuracy', 0) if enhanced_result else 0
            baseline_acc = baseline_result.get('accuracy', 0) if baseline_result else 0
            logger.info(f"✅ Completed {book}: Enhanced={enhanced_acc:.1%}, Baseline={baseline_acc:.1%}")
        
        # Calculate aggregated results
        self._calculate_aggregated_results(enhanced_results, baseline_results)
        
        # Generate comparison summary
        self._generate_comparison_summary(enhanced_results, baseline_results)
        
        # Update system info
        self.results['system_info'].update({
            'books_tested': books,
            'total_books': len(books),
            'total_questions': len(books) * questions_per_book,
            'total_execution_time': time.time() - start_time
        })
        
        logger.info(f"✅ Multi-book benchmark completed in {time.time() - start_time:.2f} seconds")
        return self.results
    
    def _test_book_enhanced(self, book: str, max_questions: int) -> Optional[Dict[str, Any]]:
        """Test a book with contextual enhancement"""
        try:
            result = self.evaluator.evaluate_hybrid_retrieval(book, max_questions=max_questions)
            return {
                'method': 'hybrid_retrieval_enhanced',
                'book': book,
                'contextual_enhancement_used': True,
                'accuracy': result.correct_retrievals / result.total_questions,
                'dcg_at_1': result.dcg_at_1,
                'dcg_at_5': result.dcg_at_5,
                'dcg_at_10': result.dcg_at_10,
                'dcg_at_20': result.dcg_at_20,
                'total_questions': result.total_questions,
                'correct_retrievals': result.correct_retrievals
            }
        except Exception as e:
            logger.error(f"❌ Enhanced evaluation failed for {book}: {e}")
            return None
    
    def _test_book_baseline(self, book: str, max_questions: int) -> Optional[Dict[str, Any]]:
        """Test a book with baseline (Contriever)"""
        try:
            # Use the simple baseline evaluator 
            baseline_evaluator = GutenQAEvaluator()
            baseline_evaluator.load_gutenqa_dataset()
            
            # Override retrieval method to use basic baseline
            result = baseline_evaluator.evaluate_baseline_retrieval(book, max_questions=max_questions)
            return {
                'method': 'contriever_baseline',
                'book': book,
                'contextual_enhancement_used': False,
                'accuracy': result.correct_retrievals / result.total_questions,
                'dcg_at_1': result.dcg_at_1,
                'dcg_at_5': result.dcg_at_5,
                'dcg_at_10': result.dcg_at_10,
                'dcg_at_20': result.dcg_at_20,
                'total_questions': result.total_questions,
                'correct_retrievals': result.correct_retrievals
            }
        except Exception as e:
            logger.error(f"❌ Baseline evaluation failed for {book}: {e}")
            return None
    
    def _calculate_aggregated_results(self, enhanced_results: List[Dict], baseline_results: List[Dict]):
        """Calculate aggregated statistics across all books"""
        
        if not enhanced_results or not baseline_results:
            return
            
        # Enhanced metrics
        enhanced_accuracies = [r['accuracy'] for r in enhanced_results]
        enhanced_dcg_1 = [r['dcg_at_1'] for r in enhanced_results]
        enhanced_dcg_5 = [r['dcg_at_5'] for r in enhanced_results]
        enhanced_dcg_10 = [r['dcg_at_10'] for r in enhanced_results]
        enhanced_dcg_20 = [r['dcg_at_20'] for r in enhanced_results]
        
        # Baseline metrics
        baseline_accuracies = [r['accuracy'] for r in baseline_results]
        baseline_dcg_1 = [r['dcg_at_1'] for r in baseline_results]
        baseline_dcg_5 = [r['dcg_at_5'] for r in baseline_results]
        baseline_dcg_10 = [r['dcg_at_10'] for r in baseline_results]
        baseline_dcg_20 = [r['dcg_at_20'] for r in baseline_results]
        
        self.results['aggregated_results'] = {
            'enhanced': {
                'accuracy': {
                    'mean': mean(enhanced_accuracies),
                    'std': stdev(enhanced_accuracies) if len(enhanced_accuracies) > 1 else 0,
                    'min': min(enhanced_accuracies),
                    'max': max(enhanced_accuracies)
                },
                'dcg_at_1': {
                    'mean': mean(enhanced_dcg_1),
                    'std': stdev(enhanced_dcg_1) if len(enhanced_dcg_1) > 1 else 0,
                    'min': min(enhanced_dcg_1),
                    'max': max(enhanced_dcg_1)
                },
                'dcg_at_5': {
                    'mean': mean(enhanced_dcg_5),
                    'std': stdev(enhanced_dcg_5) if len(enhanced_dcg_5) > 1 else 0,
                    'min': min(enhanced_dcg_5),
                    'max': max(enhanced_dcg_5)
                },
                'dcg_at_10': {
                    'mean': mean(enhanced_dcg_10),
                    'std': stdev(enhanced_dcg_10) if len(enhanced_dcg_10) > 1 else 0,
                    'min': min(enhanced_dcg_10),
                    'max': max(enhanced_dcg_10)
                },
                'dcg_at_20': {
                    'mean': mean(enhanced_dcg_20),
                    'std': stdev(enhanced_dcg_20) if len(enhanced_dcg_20) > 1 else 0,
                    'min': min(enhanced_dcg_20),
                    'max': max(enhanced_dcg_20)
                }
            },
            'baseline': {
                'accuracy': {
                    'mean': mean(baseline_accuracies),
                    'std': stdev(baseline_accuracies) if len(baseline_accuracies) > 1 else 0,
                    'min': min(baseline_accuracies),
                    'max': max(baseline_accuracies)
                },
                'dcg_at_1': {
                    'mean': mean(baseline_dcg_1),
                    'std': stdev(baseline_dcg_1) if len(baseline_dcg_1) > 1 else 0,
                    'min': min(baseline_dcg_1),
                    'max': max(baseline_dcg_1)
                },
                'dcg_at_5': {
                    'mean': mean(baseline_dcg_5),
                    'std': stdev(baseline_dcg_5) if len(baseline_dcg_5) > 1 else 0,
                    'min': min(baseline_dcg_5),
                    'max': max(baseline_dcg_5)
                },
                'dcg_at_10': {
                    'mean': mean(baseline_dcg_10),
                    'std': stdev(baseline_dcg_10) if len(baseline_dcg_10) > 1 else 0,
                    'min': min(baseline_dcg_10),
                    'max': max(baseline_dcg_10)
                },
                'dcg_at_20': {
                    'mean': mean(baseline_dcg_20),
                    'std': stdev(baseline_dcg_20) if len(baseline_dcg_20) > 1 else 0,
                    'min': min(baseline_dcg_20),
                    'max': max(baseline_dcg_20)
                }
            }
        }
        
    def _generate_comparison_summary(self, enhanced_results: List[Dict], baseline_results: List[Dict]):
        """Generate summary comparing enhanced vs baseline results"""
        
        if not enhanced_results or not baseline_results:
            return
            
        agg = self.results['aggregated_results']
        enhanced_acc = agg['enhanced']['accuracy']['mean']
        baseline_acc = agg['baseline']['accuracy']['mean']
        
        enhanced_dcg1 = agg['enhanced']['dcg_at_1']['mean']
        baseline_dcg1 = agg['baseline']['dcg_at_1']['mean']
        
        enhanced_dcg5 = agg['enhanced']['dcg_at_5']['mean']
        baseline_dcg5 = agg['baseline']['dcg_at_5']['mean']
        
        enhanced_dcg10 = agg['enhanced']['dcg_at_10']['mean']
        baseline_dcg10 = agg['baseline']['dcg_at_10']['mean']
        
        enhanced_dcg20 = agg['enhanced']['dcg_at_20']['mean']
        baseline_dcg20 = agg['baseline']['dcg_at_20']['mean']
        
        self.results['comparison_summary'] = {
            'accuracy_improvement': {
                'enhanced': enhanced_acc,
                'baseline': baseline_acc,
                'absolute_improvement': enhanced_acc - baseline_acc,
                'relative_improvement': ((enhanced_acc - baseline_acc) / baseline_acc * 100) if baseline_acc > 0 else 0
            },
            'dcg_improvements': {
                'dcg_at_1': {
                    'enhanced': enhanced_dcg1,
                    'baseline': baseline_dcg1,
                    'absolute_improvement': enhanced_dcg1 - baseline_dcg1,
                    'relative_improvement': ((enhanced_dcg1 - baseline_dcg1) / baseline_dcg1 * 100) if baseline_dcg1 > 0 else 0
                },
                'dcg_at_5': {
                    'enhanced': enhanced_dcg5,
                    'baseline': baseline_dcg5,
                    'absolute_improvement': enhanced_dcg5 - baseline_dcg5,
                    'relative_improvement': ((enhanced_dcg5 - baseline_dcg5) / baseline_dcg5 * 100) if baseline_dcg5 > 0 else 0
                },
                'dcg_at_10': {
                    'enhanced': enhanced_dcg10,
                    'baseline': baseline_dcg10,
                    'absolute_improvement': enhanced_dcg10 - baseline_dcg10,
                    'relative_improvement': ((enhanced_dcg10 - baseline_dcg10) / baseline_dcg10 * 100) if baseline_dcg10 > 0 else 0
                },
                'dcg_at_20': {
                    'enhanced': enhanced_dcg20,
                    'baseline': baseline_dcg20,
                    'absolute_improvement': enhanced_dcg20 - baseline_dcg20,
                    'relative_improvement': ((enhanced_dcg20 - baseline_dcg20) / baseline_dcg20 * 100) if baseline_dcg20 > 0 else 0
                }
            },
            'books_where_enhanced_better': sum(1 for i in range(len(enhanced_results)) 
                                              if enhanced_results[i]['accuracy'] > baseline_results[i]['accuracy']),
            'total_books_tested': len(enhanced_results),
            'improvement_consistency': (sum(1 for i in range(len(enhanced_results)) 
                                          if enhanced_results[i]['accuracy'] > baseline_results[i]['accuracy']) / len(enhanced_results) * 100)
        }
    
    def save_results(self, filename: Optional[str] = None) -> str:
        """Save results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"multi_book_benchmark_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"📁 Results saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
            return ""
    
    def print_summary(self):
        """Print comprehensive summary of results"""
        print("\n" + "="*80)
        print("MULTI-BOOK CONTEXTUAL ENHANCEMENT BENCHMARK RESULTS")
        print("="*80)
        
        sys_info = self.results['system_info']
        print(f"📚 Books tested: {sys_info['total_books']}")
        print(f"❓ Total questions: {sys_info['total_questions']}")
        print(f"⏱️ Total time: {sys_info.get('total_execution_time', 0):.2f} seconds")
        
        if 'aggregated_results' in self.results:
            agg = self.results['aggregated_results']
            
            print(f"\n📊 AGGREGATED RESULTS:")
            print(f"   Enhanced Accuracy: {agg['enhanced']['accuracy']['mean']:.1%} ± {agg['enhanced']['accuracy']['std']:.1%}")
            print(f"   Baseline Accuracy: {agg['baseline']['accuracy']['mean']:.1%} ± {agg['baseline']['accuracy']['std']:.1%}")
            
            print(f"\n📈 PERFORMANCE IMPROVEMENTS:")
            if 'comparison_summary' in self.results:
                comp = self.results['comparison_summary']
                print(f"   Accuracy: {comp['accuracy_improvement']['relative_improvement']:+.1f}% ({comp['accuracy_improvement']['absolute_improvement']:+.1%})")
                print(f"   DCG@1: {comp['dcg_improvements']['dcg_at_1']['relative_improvement']:+.1f}%")
                print(f"   DCG@5: {comp['dcg_improvements']['dcg_at_5']['relative_improvement']:+.1f}%")
                print(f"   DCG@10: {comp['dcg_improvements']['dcg_at_10']['relative_improvement']:+.1f}%")
                print(f"   DCG@20: {comp['dcg_improvements']['dcg_at_20']['relative_improvement']:+.1f}%")
                
                print(f"\n🎯 CONSISTENCY:")
                print(f"   Books where enhanced > baseline: {comp['books_where_enhanced_better']}/{comp['total_books_tested']}")
                print(f"   Improvement consistency: {comp['improvement_consistency']:.1f}%")
        
        print(f"\n📖 INDIVIDUAL BOOK RESULTS:")
        for book, results in self.results['book_results'].items():
            enhanced = results.get('enhanced', {})
            baseline = results.get('baseline', {})
            
            if enhanced and baseline:
                improvement = (enhanced['accuracy'] - baseline['accuracy']) * 100
                print(f"   {book[:50]:50} | Enhanced: {enhanced['accuracy']:.1%} | Baseline: {baseline['accuracy']:.1%} | Δ: {improvement:+.1f}%")
        
        print("="*80)


def main():
    """Main benchmark execution"""
    logger.info("🚀 Starting Multi-Book Contextual Enhancement Benchmark")
    
    # Select interesting books for testing
    test_books = [
        "A Christmas Carol - Charles Dickens",
        "A Study in Scarlet - Arthur Conan Doyle", 
        "Alice's Adventures in Wonderland - Lewis Carroll",
        "Adventures of Huckleberry Finn - Mark Twain",
        "A Tale of Two Cities - Charles Dickens",
        "A Portrait of the Artist as a Young Man - James Joyce",
        "A Connecticut Yankee in King Arthur's Court - Mark Twain",
        "A Room with a View - E. M. Forster"
    ]
    
    # Convert to the format used in the dataset
    formatted_books = []
    for book in test_books:
        formatted_book = book.replace(" - ", "_-_").replace(" ", "_")
        formatted_books.append(formatted_book)
    
    benchmark = MultiBookBenchmark()
    
    try:
        # Run multi-book benchmark
        results = benchmark.run_multi_book_benchmark(
            books=formatted_books,
            max_books=8,
            questions_per_book=30
        )
        
        # Save results
        filename = benchmark.save_results()
        
        # Print summary
        benchmark.print_summary()
        
        # Print file location
        if filename:
            print(f"\n📁 Detailed results saved to: {filename}")
        
        logger.info("✅ Multi-book benchmark completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Multi-book benchmark failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 