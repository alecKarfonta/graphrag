#!/usr/bin/env python3
"""
Test script for the Graph RAG evaluation framework and automated test suite.
This script validates that all evaluation components are working correctly.
"""

import sys
import os
import time
import json
from typing import Dict, Any

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graphrag_evaluator import GraphRAGEvaluator
from automated_test_suite import AutomatedTestSuite

def test_evaluation_framework():
    """Test the evaluation framework components."""
    print("🧪 Testing Graph RAG Evaluation Framework")
    print("=" * 50)
    
    try:
        # Initialize evaluator
        print("1. Initializing GraphRAG Evaluator...")
        evaluator = GraphRAGEvaluator()
        print("✅ Evaluator initialized successfully")
        
        # Test entity extraction evaluation
        print("\n2. Testing Entity Extraction Evaluation...")
        test_documents = [
            "The Honda Civic has a 1.5L turbocharged engine that produces 180 horsepower.",
            "Toyota Camry features a 2.5L four-cylinder engine with 203 horsepower."
        ]
        
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
        
        entity_results = evaluator.evaluate_entity_extraction(test_documents, ground_truth)
        print(f"✅ Entity extraction evaluation completed")
        print(f"   Overall F1 Score: {entity_results['overall'].f1_score:.3f}")
        
        # Test query response evaluation
        print("\n3. Testing Query Response Evaluation...")
        test_queries = [
            "What is the engine displacement of the Honda Civic?",
            "How many horsepower does the Toyota Camry have?"
        ]
        expected_answers = [
            "The Honda Civic has a 1.5L turbocharged engine.",
            "The Toyota Camry has 203 horsepower."
        ]
        
        query_results = evaluator.evaluate_query_responses(test_queries, expected_answers)
        print(f"✅ Query response evaluation completed")
        print(f"   Overall Accuracy: {query_results['overall'].accuracy:.3f}")
        
        # Test graph completeness evaluation
        print("\n4. Testing Graph Completeness Evaluation...")
        graph_results = evaluator.evaluate_graph_completeness()
        print(f"✅ Graph completeness evaluation completed")
        print(f"   Total Nodes: {graph_results.get('total_nodes', 0)}")
        print(f"   Total Relationships: {graph_results.get('total_relationships', 0)}")
        
        # Test retrieval relevance evaluation
        print("\n5. Testing Retrieval Relevance Evaluation...")
        relevance_results = evaluator.evaluate_retrieval_relevance(test_queries, [0.8, 0.7])
        print(f"✅ Retrieval relevance evaluation completed")
        print(f"   Overall Accuracy: {relevance_results['overall'].accuracy:.3f}")
        
        # Generate evaluation report
        print("\n6. Generating Evaluation Report...")
        all_results = {
            'entity_extraction': entity_results,
            'query_responses': query_results,
            'graph_completeness': graph_results,
            'retrieval_relevance': relevance_results
        }
        
        report = evaluator.generate_evaluation_report(all_results)
        print("✅ Evaluation report generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Evaluation framework test failed: {e}")
        return False

def test_automated_test_suite():
    """Test the automated test suite."""
    print("\n🧪 Testing Automated Test Suite")
    print("=" * 50)
    
    try:
        # Initialize test suite
        print("1. Initializing Automated Test Suite...")
        test_suite = AutomatedTestSuite()
        print("✅ Test suite initialized successfully")
        
        # Run unit tests
        print("\n2. Running Unit Tests...")
        unit_results = test_suite.run_unit_tests()
        print(f"✅ Unit tests completed")
        print(f"   Success Rate: {unit_results['success_rate']:.1%}")
        
        # Run integration tests
        print("\n3. Running Integration Tests...")
        integration_results = test_suite.run_integration_tests()
        print(f"✅ Integration tests completed")
        print(f"   Success Rate: {integration_results['success_rate']:.1%}")
        
        # Run performance tests
        print("\n4. Running Performance Tests...")
        performance_results = test_suite.run_performance_tests()
        print(f"✅ Performance tests completed")
        print(f"   Performance Score: {performance_results['performance_score']:.1%}")
        
        # Run quality tests
        print("\n5. Running Quality Tests...")
        quality_results = test_suite.run_quality_tests()
        print(f"✅ Quality tests completed")
        print(f"   Quality Score: {quality_results['quality_score']:.1%}")
        
        # Run comprehensive tests
        print("\n6. Running Comprehensive Test Suite...")
        comprehensive_results = test_suite.run_comprehensive_tests()
        print(f"✅ Comprehensive test suite completed")
        print(f"   Overall Score: {comprehensive_results['overall_score']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Automated test suite test failed: {e}")
        return False

def test_integration():
    """Test integration between evaluation framework and test suite."""
    print("\n🧪 Testing Integration")
    print("=" * 50)
    
    try:
        # Test that evaluation framework can be used within test suite
        print("1. Testing Evaluation Framework Integration...")
        test_suite = AutomatedTestSuite()
        
        # Run quality tests that use the evaluator
        quality_results = test_suite.run_quality_tests()
        
        # Check that quality tests used the evaluator
        if 'entity_extraction_accuracy' in quality_results['results']:
            print("✅ Evaluation framework integrated with test suite")
        else:
            print("❌ Evaluation framework not properly integrated")
            return False
        
        # Test report generation
        print("\n2. Testing Report Generation...")
        comprehensive_results = test_suite.run_comprehensive_tests()
        
        # Check that reports were generated
        if os.path.exists('test_results.json') and os.path.exists('test_summary.txt'):
            print("✅ Test reports generated successfully")
        else:
            print("❌ Test reports not generated")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Starting Graph RAG Evaluation Framework Tests")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run all tests
    tests = [
        ("Evaluation Framework", test_evaluation_framework),
        ("Automated Test Suite", test_automated_test_suite),
        ("Integration", test_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results[test_name] = success
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            print(f"\n❌ FAILED: {test_name} - {e}")
            results[test_name] = False
    
    # Summary
    total_time = time.time() - start_time
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    print(f"Total Time: {total_time:.2f}s")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Phase 1 is complete and ready for production.")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 