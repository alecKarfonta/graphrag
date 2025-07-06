import unittest
import time
import json
import os
import tempfile
from typing import List, Dict, Any
from unittest.mock import Mock, patch
import logging

from graphrag_evaluator import GraphRAGEvaluator, TestCase, EvaluationResult
from entity_extractor import EntityExtractor
from hybrid_retriever import HybridRetriever
from query_processor import QueryProcessor
from knowledge_graph_builder import KnowledgeGraphBuilder
from document_processor import DocumentProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutomatedTestSuite:
    """Comprehensive automated test suite for Graph RAG system."""
    
    def __init__(self):
        """Initialize the test suite."""
        self.evaluator = GraphRAGEvaluator()
        self.test_results = {
            'unit_tests': {},
            'integration_tests': {},
            'performance_tests': {},
            'quality_tests': {}
        }
        
        # Test data
        self.sample_documents = [
            "The Honda Civic has a 1.5L turbocharged engine that produces 180 horsepower. The brake system includes ABS and electronic brake distribution.",
            "Toyota Camry features a 2.5L four-cylinder engine with 203 horsepower. The transmission is an 8-speed automatic with manual mode.",
            "Ford F-150 comes with a 3.5L EcoBoost V6 engine producing 400 horsepower. The truck has a 10-speed automatic transmission."
        ]
        
        self.sample_queries = [
            "What is the engine displacement of the Honda Civic?",
            "How many horsepower does the Toyota Camry have?",
            "What type of transmission does the Ford F-150 use?",
            "Compare the horsepower of Honda Civic and Toyota Camry",
            "What are the brake system features of the Honda Civic?"
        ]
        
        self.expected_answers = [
            "The Honda Civic has a 1.5L turbocharged engine.",
            "The Toyota Camry has 203 horsepower.",
            "The Ford F-150 has a 10-speed automatic transmission.",
            "Honda Civic has 180 horsepower, Toyota Camry has 203 horsepower.",
            "The Honda Civic brake system includes ABS and electronic brake distribution."
        ]
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests for individual components."""
        logger.info("Starting unit tests...")
        
        unit_test_results = {
            'entity_extractor': self._test_entity_extractor(),
            'hybrid_retriever': self._test_hybrid_retriever(),
            'query_processor': self._test_query_processor(),
            'knowledge_graph_builder': self._test_knowledge_graph_builder(),
            'document_processor': self._test_document_processor()
        }
        
        # Calculate overall unit test metrics
        total_tests = sum(len(result['tests']) for result in unit_test_results.values())
        passed_tests = sum(len([t for t in result['tests'] if t['passed']]) 
                          for result in unit_test_results.values())
        
        self.test_results['unit_tests'] = {
            'results': unit_test_results,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0.0
        }
        
        logger.info(f"Unit tests completed. {passed_tests}/{total_tests} tests passed.")
        return self.test_results['unit_tests']
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests for end-to-end pipeline."""
        logger.info("Starting integration tests...")
        
        integration_test_results = {
            'full_pipeline': self._test_full_pipeline(),
            'document_to_graph': self._test_document_to_graph(),
            'query_to_answer': self._test_query_to_answer(),
            'batch_processing': self._test_batch_processing()
        }
        
        # Calculate overall integration test metrics
        total_tests = len(integration_test_results)
        passed_tests = sum(1 for result in integration_test_results.values() if result['passed'])
        
        self.test_results['integration_tests'] = {
            'results': integration_test_results,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0.0
        }
        
        logger.info(f"Integration tests completed. {passed_tests}/{total_tests} tests passed.")
        return self.test_results['integration_tests']
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance and load tests."""
        logger.info("Starting performance tests...")
        
        performance_test_results = {
            'entity_extraction_performance': self._test_entity_extraction_performance(),
            'query_response_time': self._test_query_response_time(),
            'graph_construction_performance': self._test_graph_construction_performance(),
            'memory_usage': self._test_memory_usage(),
            'concurrent_requests': self._test_concurrent_requests()
        }
        
        # Calculate overall performance metrics
        avg_response_time = np.mean([result['avg_response_time'] for result in performance_test_results.values() 
                                   if 'avg_response_time' in result])
        
        self.test_results['performance_tests'] = {
            'results': performance_test_results,
            'avg_response_time': avg_response_time,
            'performance_score': self._calculate_performance_score(performance_test_results)
        }
        
        logger.info(f"Performance tests completed. Average response time: {avg_response_time:.2f}s")
        return self.test_results['performance_tests']
    
    def run_quality_tests(self) -> Dict[str, Any]:
        """Run quality and accuracy tests."""
        logger.info("Starting quality tests...")
        
        quality_test_results = {
            'entity_extraction_accuracy': self._test_entity_extraction_accuracy(),
            'query_response_accuracy': self._test_query_response_accuracy(),
            'graph_completeness': self._test_graph_completeness(),
            'retrieval_relevance': self._test_retrieval_relevance()
        }
        
        # Calculate overall quality metrics
        avg_accuracy = np.mean([result['accuracy'] for result in quality_test_results.values() 
                               if 'accuracy' in result])
        
        self.test_results['quality_tests'] = {
            'results': quality_test_results,
            'avg_accuracy': avg_accuracy,
            'quality_score': self._calculate_quality_score(quality_test_results)
        }
        
        logger.info(f"Quality tests completed. Average accuracy: {avg_accuracy:.3f}")
        return self.test_results['quality_tests']
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all test categories and generate comprehensive report."""
        logger.info("Starting comprehensive test suite...")
        
        start_time = time.time()
        
        # Run all test categories
        unit_results = self.run_unit_tests()
        integration_results = self.run_integration_tests()
        performance_results = self.run_performance_tests()
        quality_results = self.run_quality_tests()
        
        total_time = time.time() - start_time
        
        # Generate comprehensive report
        comprehensive_results = {
            'unit_tests': unit_results,
            'integration_tests': integration_results,
            'performance_tests': performance_results,
            'quality_tests': quality_results,
            'total_execution_time': total_time,
            'overall_score': self._calculate_overall_score()
        }
        
        # Generate test reports
        self.generate_test_reports(comprehensive_results)
        
        logger.info(f"Comprehensive test suite completed in {total_time:.2f}s")
        return comprehensive_results
    
    def _test_entity_extractor(self) -> Dict[str, Any]:
        """Test entity extraction functionality."""
        test_results = []
        
        try:
            # Test basic entity extraction
            test_doc = "The Honda Civic has a 1.5L engine with 180 horsepower."
            extraction_result = self.evaluator.entity_extractor.extract_entities_and_relations(test_doc)
            
            test_results.append({
                'test_name': 'basic_entity_extraction',
                'passed': len(extraction_result.entities) > 0,
                'entities_found': len(extraction_result.entities),
                'relationships_found': len(extraction_result.relationships)
            })
            
            # Test domain-specific extraction
            automotive_doc = "The brake system includes ABS and electronic brake distribution."
            automotive_result = self.evaluator.entity_extractor.extract_entities_and_relations(
                automotive_doc, domain="automotive"
            )
            
            test_results.append({
                'test_name': 'domain_specific_extraction',
                'passed': len(automotive_result.entities) > 0,
                'entities_found': len(automotive_result.entities),
                'domain': 'automotive'
            })
            
        except Exception as e:
            test_results.append({
                'test_name': 'entity_extractor',
                'passed': False,
                'error': str(e)
            })
        
        return {
            'tests': test_results,
            'component': 'entity_extractor'
        }
    
    def _test_hybrid_retriever(self) -> Dict[str, Any]:
        """Test hybrid retrieval functionality."""
        test_results = []
        
        try:
            # Test vector search
            query = "Honda Civic engine"
            vector_results = self.evaluator.hybrid_retriever.vector_search(query, top_k=5)
            
            test_results.append({
                'test_name': 'vector_search',
                'passed': len(vector_results) >= 0,
                'results_count': len(vector_results)
            })
            
            # Test query analysis
            query_analysis = self.evaluator.hybrid_retriever.analyze_query(query)
            
            test_results.append({
                'test_name': 'query_analysis',
                'passed': query_analysis.intent in ['factual', 'analytical', 'comparative'],
                'intent_detected': query_analysis.intent,
                'entities_found': len(query_analysis.entities)
            })
            
        except Exception as e:
            test_results.append({
                'test_name': 'hybrid_retriever',
                'passed': False,
                'error': str(e)
            })
        
        return {
            'tests': test_results,
            'component': 'hybrid_retriever'
        }
    
    def _test_query_processor(self) -> Dict[str, Any]:
        """Test query processing functionality."""
        test_results = []
        
        try:
            # Test basic query processing
            query = "What is the engine displacement of the Honda Civic?"
            query_analysis = self.evaluator.query_processor.get_query_analysis(query)
            
            test_results.append({
                'test_name': 'basic_query_processing',
                'passed': query_analysis is not None,
                'analysis_completed': query_analysis is not None
            })
            
        except Exception as e:
            test_results.append({
                'test_name': 'query_processor',
                'passed': False,
                'error': str(e)
            })
        
        return {
            'tests': test_results,
            'component': 'query_processor'
        }
    
    def _test_knowledge_graph_builder(self) -> Dict[str, Any]:
        """Test knowledge graph construction."""
        test_results = []
        
        try:
            # Test graph statistics
            graph_stats = self.evaluator.knowledge_graph_builder.get_graph_statistics()
            
            test_results.append({
                'test_name': 'graph_statistics',
                'passed': graph_stats is not None,
                'stats_retrieved': graph_stats is not None
            })
            
        except Exception as e:
            test_results.append({
                'test_name': 'knowledge_graph_builder',
                'passed': False,
                'error': str(e)
            })
        
        return {
            'tests': test_results,
            'component': 'knowledge_graph_builder'
        }
    
    def _test_document_processor(self) -> Dict[str, Any]:
        """Test document processing functionality."""
        test_results = []
        
        try:
            # Create temporary test document
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("This is a test document for processing.")
                temp_file = f.name
            
            # Test document processing
            processor = DocumentProcessor()
            chunks = processor.process_document(temp_file)
            
            test_results.append({
                'test_name': 'document_processing',
                'passed': len(chunks) > 0,
                'chunks_created': len(chunks)
            })
            
            # Clean up
            os.unlink(temp_file)
            
        except Exception as e:
            test_results.append({
                'test_name': 'document_processor',
                'passed': False,
                'error': str(e)
            })
        
        return {
            'tests': test_results,
            'component': 'document_processor'
        }
    
    def _test_full_pipeline(self) -> Dict[str, Any]:
        """Test the complete document-to-answer pipeline."""
        try:
            # Test with sample document and query
            test_doc = "The Honda Civic has a 1.5L turbocharged engine that produces 180 horsepower."
            test_query = "What is the engine displacement of the Honda Civic?"
            
            # Process document
            extraction_result = self.evaluator.entity_extractor.extract_entities_and_relations(test_doc)
            
            # Process query
            query_analysis = self.evaluator.query_processor.get_query_analysis(test_query)
            
            return {
                'test_name': 'full_pipeline',
                'passed': len(extraction_result.entities) > 0 and query_analysis is not None,
                'entities_extracted': len(extraction_result.entities),
                'query_processed': query_analysis is not None
            }
            
        except Exception as e:
            return {
                'test_name': 'full_pipeline',
                'passed': False,
                'error': str(e)
            }
    
    def _test_document_to_graph(self) -> Dict[str, Any]:
        """Test document processing to knowledge graph construction."""
        try:
            # Test document processing and graph construction
            test_doc = "The Toyota Camry features a 2.5L four-cylinder engine with 203 horsepower."
            
            # Extract entities
            extraction_result = self.evaluator.entity_extractor.extract_entities_and_relations(test_doc)
            
            # Add to knowledge graph
            if extraction_result.entities:
                self.evaluator.knowledge_graph_builder.add_extraction_result(extraction_result)
            
            return {
                'test_name': 'document_to_graph',
                'passed': len(extraction_result.entities) > 0,
                'entities_added': len(extraction_result.entities)
            }
            
        except Exception as e:
            return {
                'test_name': 'document_to_graph',
                'passed': False,
                'error': str(e)
            }
    
    def _test_query_to_answer(self) -> Dict[str, Any]:
        """Test query processing to answer generation."""
        try:
            # Test query processing
            test_query = "What is the horsepower of the Toyota Camry?"
            
            # Process query
            query_analysis = self.evaluator.query_processor.get_query_analysis(test_query)
            
            # Perform retrieval
            search_results = self.evaluator.hybrid_retriever.retrieve(test_query, top_k=5)
            
            return {
                'test_name': 'query_to_answer',
                'passed': query_analysis is not None and len(search_results) >= 0,
                'query_analyzed': query_analysis is not None,
                'results_retrieved': len(search_results)
            }
            
        except Exception as e:
            return {
                'test_name': 'query_to_answer',
                'passed': False,
                'error': str(e)
            }
    
    def _test_batch_processing(self) -> Dict[str, Any]:
        """Test batch processing capabilities."""
        try:
            # Test batch entity extraction
            extraction_results = self.evaluator.entity_extractor.extract_from_chunks(
                self.sample_documents[:2]
            )
            
            return {
                'test_name': 'batch_processing',
                'passed': len(extraction_results) == 2,
                'documents_processed': len(extraction_results)
            }
            
        except Exception as e:
            return {
                'test_name': 'batch_processing',
                'passed': False,
                'error': str(e)
            }
    
    def _test_entity_extraction_performance(self) -> Dict[str, Any]:
        """Test entity extraction performance."""
        try:
            start_time = time.time()
            
            # Process multiple documents
            for doc in self.sample_documents:
                self.evaluator.entity_extractor.extract_entities_and_relations(doc)
            
            total_time = time.time() - start_time
            avg_time_per_doc = total_time / len(self.sample_documents)
            
            return {
                'test_name': 'entity_extraction_performance',
                'total_time': total_time,
                'avg_time_per_doc': avg_time_per_doc,
                'documents_processed': len(self.sample_documents),
                'performance_acceptable': avg_time_per_doc < 5.0  # 5 seconds per document
            }
            
        except Exception as e:
            return {
                'test_name': 'entity_extraction_performance',
                'passed': False,
                'error': str(e)
            }
    
    def _test_query_response_time(self) -> Dict[str, Any]:
        """Test query response time."""
        try:
            response_times = []
            
            for query in self.sample_queries[:3]:  # Test first 3 queries
                start_time = time.time()
                
                # Perform retrieval
                self.evaluator.hybrid_retriever.retrieve(query, top_k=5)
                
                response_time = time.time() - start_time
                response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times)
            
            return {
                'test_name': 'query_response_time',
                'avg_response_time': avg_response_time,
                'max_response_time': max(response_times),
                'min_response_time': min(response_times),
                'performance_acceptable': avg_response_time < 2.0  # 2 seconds average
            }
            
        except Exception as e:
            return {
                'test_name': 'query_response_time',
                'passed': False,
                'error': str(e)
            }
    
    def _test_graph_construction_performance(self) -> Dict[str, Any]:
        """Test knowledge graph construction performance."""
        try:
            start_time = time.time()
            
            # Test graph statistics retrieval
            graph_stats = self.evaluator.knowledge_graph_builder.get_graph_statistics()
            
            construction_time = time.time() - start_time
            
            return {
                'test_name': 'graph_construction_performance',
                'construction_time': construction_time,
                'performance_acceptable': construction_time < 1.0  # 1 second
            }
            
        except Exception as e:
            return {
                'test_name': 'graph_construction_performance',
                'passed': False,
                'error': str(e)
            }
    
    def _test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage during operations."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform memory-intensive operations
            for doc in self.sample_documents:
                self.evaluator.entity_extractor.extract_entities_and_relations(doc)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            return {
                'test_name': 'memory_usage',
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_increase_mb': memory_increase,
                'performance_acceptable': memory_increase < 100  # 100 MB increase
            }
            
        except Exception as e:
            return {
                'test_name': 'memory_usage',
                'passed': False,
                'error': str(e)
            }
    
    def _test_concurrent_requests(self) -> Dict[str, Any]:
        """Test system performance under concurrent requests."""
        try:
            import threading
            import concurrent.futures
            
            def process_query(query):
                start_time = time.time()
                self.evaluator.hybrid_retriever.retrieve(query, top_k=5)
                return time.time() - start_time
            
            # Test with concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(process_query, query) for query in self.sample_queries[:3]]
                response_times = [future.result() for future in futures]
            
            avg_concurrent_time = sum(response_times) / len(response_times)
            
            return {
                'test_name': 'concurrent_requests',
                'avg_concurrent_time': avg_concurrent_time,
                'max_concurrent_time': max(response_times),
                'performance_acceptable': avg_concurrent_time < 3.0  # 3 seconds average
            }
            
        except Exception as e:
            return {
                'test_name': 'concurrent_requests',
                'passed': False,
                'error': str(e)
            }
    
    def _test_entity_extraction_accuracy(self) -> Dict[str, Any]:
        """Test entity extraction accuracy."""
        try:
            # Create ground truth for sample documents
            ground_truth = {
                "doc_0": [
                    {"name": "Honda Civic", "type": "COMPONENT"},
                    {"name": "1.5L", "type": "SPECIFICATION"},
                    {"name": "180 horsepower", "type": "SPECIFICATION"}
                ],
                "doc_1": [
                    {"name": "Toyota Camry", "type": "COMPONENT"},
                    {"name": "2.5L", "type": "SPECIFICATION"},
                    {"name": "203 horsepower", "type": "SPECIFICATION"}
                ]
            }
            
            # Evaluate entity extraction
            evaluation_results = self.evaluator.evaluate_entity_extraction(
                self.sample_documents[:2], ground_truth
            )
            
            overall_metrics = evaluation_results['overall']
            
            return {
                'test_name': 'entity_extraction_accuracy',
                'accuracy': overall_metrics.f1_score,
                'precision': overall_metrics.precision,
                'recall': overall_metrics.recall,
                'performance_acceptable': overall_metrics.f1_score > 0.5
            }
            
        except Exception as e:
            return {
                'test_name': 'entity_extraction_accuracy',
                'passed': False,
                'error': str(e)
            }
    
    def _test_query_response_accuracy(self) -> Dict[str, Any]:
        """Test query response accuracy."""
        try:
            # Evaluate query responses
            evaluation_results = self.evaluator.evaluate_query_responses(
                self.sample_queries[:3], self.expected_answers[:3]
            )
            
            overall_metrics = evaluation_results['overall']
            
            return {
                'test_name': 'query_response_accuracy',
                'accuracy': overall_metrics.accuracy,
                'avg_response_time': overall_metrics.additional_metrics.get('avg_response_time', 0),
                'performance_acceptable': overall_metrics.accuracy > 0.3
            }
            
        except Exception as e:
            return {
                'test_name': 'query_response_accuracy',
                'passed': False,
                'error': str(e)
            }
    
    def _test_graph_completeness(self) -> Dict[str, Any]:
        """Test knowledge graph completeness."""
        try:
            # Evaluate graph completeness
            completeness_metrics = self.evaluator.evaluate_graph_completeness()
            
            return {
                'test_name': 'graph_completeness',
                'total_nodes': completeness_metrics.get('total_nodes', 0),
                'total_relationships': completeness_metrics.get('total_relationships', 0),
                'graph_density': completeness_metrics.get('graph_density', 0),
                'performance_acceptable': completeness_metrics.get('total_nodes', 0) > 0
            }
            
        except Exception as e:
            return {
                'test_name': 'graph_completeness',
                'passed': False,
                'error': str(e)
            }
    
    def _test_retrieval_relevance(self) -> Dict[str, Any]:
        """Test retrieval relevance."""
        try:
            # Test retrieval relevance
            relevance_scores = [0.8, 0.7, 0.9]  # Expected relevance scores
            evaluation_results = self.evaluator.evaluate_retrieval_relevance(
                self.sample_queries[:3], relevance_scores
            )
            
            overall_metrics = evaluation_results['overall']
            
            return {
                'test_name': 'retrieval_relevance',
                'accuracy': overall_metrics.accuracy,
                'avg_relevance': overall_metrics.additional_metrics.get('avg_relevance_score', 0),
                'performance_acceptable': overall_metrics.accuracy > 0.5
            }
            
        except Exception as e:
            return {
                'test_name': 'retrieval_relevance',
                'passed': False,
                'error': str(e)
            }
    
    def _calculate_performance_score(self, performance_results: Dict[str, Any]) -> float:
        """Calculate overall performance score."""
        acceptable_tests = sum(1 for result in performance_results.values() 
                             if result.get('performance_acceptable', False))
        total_tests = len(performance_results)
        
        return acceptable_tests / total_tests if total_tests > 0 else 0.0
    
    def _calculate_quality_score(self, quality_results: Dict[str, Any]) -> float:
        """Calculate overall quality score."""
        accuracies = [result.get('accuracy', 0) for result in quality_results.values() 
                     if 'accuracy' in result]
        
        return sum(accuracies) / len(accuracies) if accuracies else 0.0
    
    def _calculate_overall_score(self) -> float:
        """Calculate overall system score."""
        unit_score = self.test_results['unit_tests'].get('success_rate', 0.0)
        integration_score = self.test_results['integration_tests'].get('success_rate', 0.0)
        performance_score = self.test_results['performance_tests'].get('performance_score', 0.0)
        quality_score = self.test_results['quality_tests'].get('quality_score', 0.0)
        
        # Weighted average
        overall_score = (unit_score * 0.3 + integration_score * 0.3 + 
                        performance_score * 0.2 + quality_score * 0.2)
        
        return overall_score
    
    def generate_test_reports(self, results: Dict[str, Any]):
        """Generate detailed test reports."""
        # Generate JSON report
        with open('test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Generate summary report
        summary = self._generate_summary_report(results)
        with open('test_summary.txt', 'w') as f:
            f.write(summary)
        
        logger.info("Test reports generated: test_results.json, test_summary.txt")
    
    def _generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate a human-readable summary report."""
        summary = []
        summary.append("=" * 80)
        summary.append("GRAPH RAG SYSTEM TEST SUMMARY")
        summary.append("=" * 80)
        summary.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")
        
        # Unit Tests Summary
        unit_tests = results.get('unit_tests', {})
        summary.append("UNIT TESTS")
        summary.append("-" * 20)
        summary.append(f"Total Tests: {unit_tests.get('total_tests', 0)}")
        summary.append(f"Passed Tests: {unit_tests.get('passed_tests', 0)}")
        summary.append(f"Success Rate: {unit_tests.get('success_rate', 0):.1%}")
        summary.append("")
        
        # Integration Tests Summary
        integration_tests = results.get('integration_tests', {})
        summary.append("INTEGRATION TESTS")
        summary.append("-" * 20)
        summary.append(f"Total Tests: {integration_tests.get('total_tests', 0)}")
        summary.append(f"Passed Tests: {integration_tests.get('passed_tests', 0)}")
        summary.append(f"Success Rate: {integration_tests.get('success_rate', 0):.1%}")
        summary.append("")
        
        # Performance Tests Summary
        performance_tests = results.get('performance_tests', {})
        summary.append("PERFORMANCE TESTS")
        summary.append("-" * 20)
        summary.append(f"Average Response Time: {performance_tests.get('avg_response_time', 0):.2f}s")
        summary.append(f"Performance Score: {performance_tests.get('performance_score', 0):.1%}")
        summary.append("")
        
        # Quality Tests Summary
        quality_tests = results.get('quality_tests', {})
        summary.append("QUALITY TESTS")
        summary.append("-" * 20)
        summary.append(f"Average Accuracy: {quality_tests.get('avg_accuracy', 0):.1%}")
        summary.append(f"Quality Score: {quality_tests.get('quality_score', 0):.1%}")
        summary.append("")
        
        # Overall Score
        overall_score = results.get('overall_score', 0)
        summary.append("OVERALL SYSTEM SCORE")
        summary.append("-" * 20)
        summary.append(f"Overall Score: {overall_score:.1%}")
        summary.append("")
        
        summary.append("=" * 80)
        
        return "\n".join(summary)

# Import numpy for calculations
import numpy as np 