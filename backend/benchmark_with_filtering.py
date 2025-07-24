#!/usr/bin/env python3
"""
Benchmark script to evaluate GraphRAG with Contextual Enhancement
This script evaluates the performance improvements from the contextual enhancement system
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gutenqa_evaluator import GutenQAEvaluator, format_retrieval_report
from hybrid_retriever import HybridRetriever
from graphrag_evaluator import GraphRAGEvaluator
from automated_test_suite import AutomatedTestSuite

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContextualEnhancementBenchmark:
    """
    Comprehensive benchmark for GraphRAG with Contextual Enhancement
    """
    
    def __init__(self):
        """Initialize the benchmark system"""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'contextual_enhancement_available': False,
                'baseline_model': 'HybridRetriever (Standard)',
                'enhanced_model': 'HybridRetriever (Contextual Enhancement)',
                'embedding_model': 'all-MiniLM-L6-v2'
            },
            'gutenqa_results': {},
            'performance_metrics': {},
            'quality_metrics': {},
            'comparison_summary': {}
        }
        
        # Initialize evaluators
        try:
            self.gutenqa_evaluator = GutenQAEvaluator()
            self.graphrag_evaluator = GraphRAGEvaluator()
            self.test_suite = AutomatedTestSuite()
            
            # Check if contextual enhancement is available
            try:
                from contextual_enhancer import ContextualEnhancer
                self.contextual_enhancement_available = True
            except ImportError:
                self.contextual_enhancement_available = False
            
            self.results['system_info']['contextual_enhancement_available'] = self.contextual_enhancement_available
            
            logger.info("✅ Benchmark components initialized successfully")
            logger.info(f"📊 Contextual enhancement available: {self.contextual_enhancement_available}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize benchmark components: {e}")
            raise
    
    def run_comprehensive_benchmark(self, test_book: str = "A Christmas Carol") -> Dict[str, Any]:
        """
        Run comprehensive benchmark comparing standard vs contextual enhancement retrieval
        
        Args:
            test_book: Book to use for evaluation (default: A Christmas Carol)
            
        Returns:
            Comprehensive benchmark results
        """
        logger.info(f"🚀 Starting contextual enhancement benchmark for '{test_book}'")
        start_time = time.time()
        
        # Step 1: Load and verify dataset
        if not self._load_dataset():
            logger.error("❌ Failed to load GutenQA dataset")
            return self.results
        
        # Step 2: Verify test book availability
        available_books = self.gutenqa_evaluator.get_available_books()
        if test_book not in available_books:
            logger.warning(f"⚠️ '{test_book}' not found. Using first available book.")
            if available_books:
                test_book = available_books[0]
            else:
                logger.error("❌ No books available for testing")
                return self.results
        
        logger.info(f"📖 Using book: {test_book}")
        
        # Step 3: Run standard evaluation (without contextual enhancement)
        logger.info("🔍 Running standard evaluation...")
        standard_results = self._run_standard_evaluation(test_book)
        
        # Step 4: Run enhanced evaluation (with contextual enhancement)
        logger.info("🔍 Running enhanced evaluation with contextual enhancement...")
        enhanced_results = self._run_enhanced_evaluation(test_book)
        
        # Step 5: Run system quality tests
        logger.info("🔍 Running system quality tests...")
        quality_results = self._run_quality_tests()
        
        # Step 6: Compare results and generate report
        logger.info("📊 Generating comparison report...")
        comparison_results = self._generate_comparison_report(standard_results, enhanced_results)
        
        # Step 7: Compile final results
        total_time = time.time() - start_time
        self.results.update({
            'test_book': test_book,
            'standard_results': standard_results,
            'enhanced_results': enhanced_results,
            'quality_results': quality_results,
            'comparison_summary': comparison_results,
            'total_execution_time': total_time
        })
        
        logger.info(f"✅ Benchmark completed in {total_time:.2f} seconds")
        return self.results
    
    def _load_dataset(self) -> bool:
        """Load the GutenQA dataset"""
        try:
            success = self.gutenqa_evaluator.load_gutenqa_dataset()
            if success:
                stats = self.gutenqa_evaluator.get_dataset_statistics()
                self.results['dataset_stats'] = stats
                logger.info(f"📊 Dataset loaded: {stats.get('total_books', 0)} books, {stats.get('total_questions', 0)} questions")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load dataset: {e}")
            return False
    
    def _run_standard_evaluation(self, test_book: str) -> Dict[str, Any]:
        """Run standard hybrid retrieval evaluation (without contextual enhancement)"""
        try:
            logger.info("Running standard hybrid retrieval evaluation...")
            
            # Create a custom evaluator that forces standard processing
            standard_evaluator = self._create_standard_evaluator()
            
            # Run evaluation with standard processing
            standard_result = standard_evaluator.evaluate_hybrid_retrieval(test_book, max_questions=50)
            
            return {
                'method': 'hybrid_retrieval_standard',
                'contextual_enhancement_used': False,
                'dcg_at_1': standard_result.dcg_at_1,
                'dcg_at_2': standard_result.dcg_at_2,
                'dcg_at_5': standard_result.dcg_at_5,
                'dcg_at_10': standard_result.dcg_at_10,
                'dcg_at_20': standard_result.dcg_at_20,
                'accuracy': standard_result.correct_retrievals / standard_result.total_questions,
                'total_questions': standard_result.total_questions,
                'correct_retrievals': standard_result.correct_retrievals
            }
        except Exception as e:
            logger.error(f"❌ Standard evaluation failed: {e}")
            return {'error': str(e)}
    
    def _run_enhanced_evaluation(self, test_book: str) -> Dict[str, Any]:
        """Run enhanced hybrid retrieval evaluation (with contextual enhancement)"""
        try:
            logger.info("Running enhanced hybrid retrieval evaluation...")
            
            if not self.contextual_enhancement_available:
                logger.warning("⚠️ Contextual enhancement not available, using standard evaluation")
                return self._run_standard_evaluation(test_book)
            
            # Use the regular evaluator which should use contextual enhancement if available
            enhanced_result = self.gutenqa_evaluator.evaluate_hybrid_retrieval(test_book, max_questions=50)
            
            return {
                'method': 'hybrid_retrieval_enhanced',
                'contextual_enhancement_used': True,
                'dcg_at_1': enhanced_result.dcg_at_1,
                'dcg_at_2': enhanced_result.dcg_at_2,
                'dcg_at_5': enhanced_result.dcg_at_5,
                'dcg_at_10': enhanced_result.dcg_at_10,
                'dcg_at_20': enhanced_result.dcg_at_20,
                'accuracy': enhanced_result.correct_retrievals / enhanced_result.total_questions,
                'total_questions': enhanced_result.total_questions,
                'correct_retrievals': enhanced_result.correct_retrievals
            }
        except Exception as e:
            logger.error(f"❌ Enhanced evaluation failed: {e}")
            return {'error': str(e)}
    
    def _create_standard_evaluator(self) -> GutenQAEvaluator:
        """Create a custom evaluator that forces standard processing (no contextual enhancement)"""
        # Create a custom evaluator that bypasses contextual enhancement
        class StandardGutenQAEvaluator(GutenQAEvaluator):
            def __init__(self):
                super().__init__()
                # Override the retriever to force standard processing
                self.retriever = self._create_standard_retriever()
            
            def _create_standard_retriever(self):
                """Create a retriever that doesn't use contextual enhancement"""
                # Import here to avoid circular imports
                from hybrid_retriever import HybridRetriever
                
                # Create a standard retriever
                retriever = HybridRetriever()
                
                # Monkey patch the add_document_chunks method to bypass contextual enhancement
                original_add_chunks = retriever.add_document_chunks
                
                def add_chunks_without_enhancement(chunks):
                    """Add chunks without contextual enhancement"""
                    try:
                        # Force standard processing by directly calling _prepare_standard_points
                        points = retriever._prepare_standard_points(chunks)
                        
                        # Store points in Qdrant
                        retriever.qdrant_client.upsert(
                            collection_name=retriever.collection_name,
                            points=points
                        )
                        
                        print(f"Added {len(points)} chunks to vector store (standard processing)")
                        
                        # Add to BM25 index if available
                        if hasattr(retriever, 'bm25') and retriever.bm25:
                            retriever._add_to_bm25_index(chunks)
                            print(f"Added {len(chunks)} documents to BM25 index (standard processing)")
                        
                    except Exception as e:
                        print(f"Error in standard processing: {e}")
                        # Fallback to original method
                        return original_add_chunks(chunks)
                
                # Replace the method
                retriever.add_document_chunks = add_chunks_without_enhancement
                
                return retriever
        
        return StandardGutenQAEvaluator()
    
    def _run_quality_tests(self) -> Dict[str, Any]:
        """Run comprehensive quality tests"""
        try:
            logger.info("Running comprehensive quality tests...")
            quality_results = self.test_suite.run_quality_tests()
            
            return {
                'entity_extraction_accuracy': quality_results['results'].get('entity_extraction_accuracy', {}),
                'query_response_accuracy': quality_results['results'].get('query_response_accuracy', {}),
                'graph_completeness': quality_results['results'].get('graph_completeness', {}),
                'retrieval_relevance': quality_results['results'].get('retrieval_relevance', {}),
                'overall_quality_score': quality_results.get('quality_score', 0.0)
            }
        except Exception as e:
            logger.error(f"❌ Quality tests failed: {e}")
            return {'error': str(e)}
    
    def _generate_comparison_report(self, standard_results: Dict, enhanced_results: Dict) -> Dict[str, Any]:
        """Generate detailed comparison report"""
        if 'error' in standard_results or 'error' in enhanced_results:
            return {'error': 'Cannot compare due to evaluation errors'}
        
        comparison = {
            'accuracy_improvement': {},
            'dcg_improvements': {},
            'contextual_enhancement_impact': {},
            'performance_summary': {}
        }
        
        # Calculate improvements
        standard_accuracy = standard_results.get('accuracy', 0)
        enhanced_accuracy = enhanced_results.get('accuracy', 0)
        
        if standard_accuracy > 0:
            accuracy_improvement = (enhanced_accuracy - standard_accuracy) / standard_accuracy * 100
            comparison['accuracy_improvement'] = {
                'standard': standard_accuracy,
                'enhanced': enhanced_accuracy,
                'improvement_percent': accuracy_improvement,
                'improvement_absolute': enhanced_accuracy - standard_accuracy
            }
        
        # Calculate DCG improvements
        dcg_metrics = ['dcg_at_1', 'dcg_at_2', 'dcg_at_5', 'dcg_at_10', 'dcg_at_20']
        for metric in dcg_metrics:
            standard_dcg = standard_results.get(metric, 0)
            enhanced_dcg = enhanced_results.get(metric, 0)
            
            if standard_dcg > 0:
                improvement = (enhanced_dcg - standard_dcg) / standard_dcg * 100
                comparison['dcg_improvements'][metric] = {
                    'standard': standard_dcg,
                    'enhanced': enhanced_dcg,
                    'improvement_percent': improvement
                }
        
        # Contextual enhancement impact
        comparison['contextual_enhancement_impact'] = {
            'standard_method': standard_results.get('method', 'unknown'),
            'enhanced_method': enhanced_results.get('method', 'unknown'),
            'contextual_enhancement_used': enhanced_results.get('contextual_enhancement_used', False),
            'enhancement_available': self.contextual_enhancement_available,
            'improvement_attributed_to_enhancement': enhanced_results.get('contextual_enhancement_used', False)
        }
        
        # Performance summary
        comparison['performance_summary'] = {
            'standard_method': standard_results.get('method', 'unknown'),
            'enhanced_method': enhanced_results.get('method', 'unknown'),
            'contextual_enhancement_enabled': enhanced_results.get('contextual_enhancement_used', False),
            'total_questions_tested': enhanced_results.get('total_questions', 0),
            'standard_correct': standard_results.get('correct_retrievals', 0),
            'enhanced_correct': enhanced_results.get('correct_retrievals', 0),
            'improvement_in_correct_answers': enhanced_results.get('correct_retrievals', 0) - standard_results.get('correct_retrievals', 0)
        }
        
        return comparison
    
    def save_results(self, filename: Optional[str] = None) -> str:
        """Save benchmark results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"contextual_enhancement_benchmark_{timestamp}.json"
        
        try:
            # Convert numpy types to native Python types for JSON serialization
            def convert_numpy_types(obj):
                if hasattr(obj, 'item'):  # numpy scalar
                    return obj.item()
                elif hasattr(obj, 'tolist'):  # numpy array
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_numpy_types(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_types(item) for item in obj]
                else:
                    return obj
            
            serializable_results = convert_numpy_types(self.results)
            
            with open(filename, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            logger.info(f"📁 Results saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
            return ""
    
    def print_summary(self):
        """Print a summary of the benchmark results"""
        print("\n" + "="*80)
        print("GRAPHRAG CONTEXTUAL ENHANCEMENT BENCHMARK RESULTS")
        print("="*80)
        
        if 'test_book' in self.results:
            print(f"📖 Test Book: {self.results['test_book']}")
        
        if 'dataset_stats' in self.results:
            stats = self.results['dataset_stats']
            print(f"📊 Dataset: {stats.get('total_books', 0)} books, {stats.get('total_questions', 0)} questions")
        
        enhancement_available = self.results['system_info'].get('contextual_enhancement_available', False)
        print(f"🔧 Contextual Enhancement: {'✅ AVAILABLE' if enhancement_available else '❌ NOT AVAILABLE'}")
        
        # Print comparison results
        if 'comparison_summary' in self.results:
            comp = self.results['comparison_summary']
            
            if 'accuracy_improvement' in comp:
                acc_imp = comp['accuracy_improvement']
                print(f"\n📈 ACCURACY RESULTS:")
                print(f"   Standard (no enhancement):  {acc_imp['standard']:.3f} ({acc_imp['standard']*100:.1f}%)")
                print(f"   Enhanced (with enhancement): {acc_imp['enhanced']:.3f} ({acc_imp['enhanced']*100:.1f}%)")
                print(f"   Improvement from enhancement: {acc_imp['improvement_percent']:+.1f}%")
            
            if 'dcg_improvements' in comp:
                print(f"\n📊 DCG IMPROVEMENTS:")
                for metric, data in comp['dcg_improvements'].items():
                    print(f"   {metric}: {data['improvement_percent']:+.1f}% ({data['standard']:.3f} → {data['enhanced']:.3f})")
            
            if 'contextual_enhancement_impact' in comp:
                impact = comp['contextual_enhancement_impact']
                print(f"\n🎯 CONTEXTUAL ENHANCEMENT IMPACT:")
                print(f"   Enhancement Available: {impact['enhancement_available']}")
                print(f"   Enhancement Used: {impact['contextual_enhancement_used']}")
                print(f"   Standard Method: {impact['standard_method']}")
                print(f"   Enhanced Method: {impact['enhanced_method']}")
                
            if 'performance_summary' in comp:
                perf = comp['performance_summary']
                print(f"\n🎯 PERFORMANCE SUMMARY:")
                print(f"   Total Questions: {perf['total_questions_tested']}")
                print(f"   Standard Correct: {perf['standard_correct']}")
                print(f"   Enhanced Correct: {perf['enhanced_correct']}")
                print(f"   Additional Correct: {perf['improvement_in_correct_answers']}")
        
        # Print quality metrics
        if 'quality_results' in self.results:
            quality = self.results['quality_results']
            print(f"\n🔍 QUALITY METRICS:")
            print(f"   Overall Quality Score: {quality.get('overall_quality_score', 0):.3f}")
            
            if 'entity_extraction_accuracy' in quality:
                ee_acc = quality['entity_extraction_accuracy']
                print(f"   Entity Extraction Accuracy: {ee_acc.get('accuracy', 0):.3f}")
            
            if 'retrieval_relevance' in quality:
                rr_acc = quality['retrieval_relevance']
                print(f"   Retrieval Relevance: {rr_acc.get('accuracy', 0):.3f}")
        
        print(f"\n⏱️  Total Execution Time: {self.results.get('total_execution_time', 0):.2f} seconds")
        print("="*80)


def main():
    """Main benchmark execution"""
    logger.info("🚀 Starting GraphRAG Contextual Enhancement Benchmark")
    
    benchmark = ContextualEnhancementBenchmark()
    
    # Run comprehensive benchmark
    try:
        results = benchmark.run_comprehensive_benchmark()
        
        # Save results
        filename = benchmark.save_results()
        
        # Print summary
        benchmark.print_summary()
        
        # Print file location
        if filename:
            print(f"\n📁 Detailed results saved to: {filename}")
        
        logger.info("✅ Benchmark completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Benchmark failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 