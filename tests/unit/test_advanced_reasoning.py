#!/usr/bin/env python3
"""
Test script for advanced reasoning features

This script tests the new Phase 2 features including:
- Query intent analysis
- Advanced reasoning engine
- Causal reasoning
- Comparative reasoning
- Multi-hop reasoning
- Enhanced query processing
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_api_endpoint(endpoint: str, data: Dict[str, Any], description: str) -> Dict[str, Any]:
    """Test an API endpoint and return the result."""
    print(f"\n🧪 Testing {description}...")
    print(f"Endpoint: {endpoint}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(f"{API_BASE}/{endpoint}", params=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {description}")
            print(f"Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return {"error": f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"error": str(e)}

def test_query_intent_analysis():
    """Test query intent analysis with various query types."""
    print("\n" + "="*60)
    print("TESTING QUERY INTENT ANALYSIS")
    print("="*60)
    
    test_queries = [
        {
            "query": "What is the relationship between engine and transmission?",
            "expected_intent": "factual"
        },
        {
            "query": "Compare the performance of electric and gasoline engines",
            "expected_intent": "comparative"
        },
        {
            "query": "How does low oil pressure cause engine damage?",
            "expected_intent": "causal"
        },
        {
            "query": "What are the steps to replace brake pads?",
            "expected_intent": "procedural"
        },
        {
            "query": "Analyze the impact of temperature on battery performance",
            "expected_intent": "analytical"
        },
        {
            "query": "What is the timeline of automotive technology evolution?",
            "expected_intent": "temporal"
        }
    ]
    
    results = []
    for test_case in test_queries:
        result = test_api_endpoint(
            "analyze-query-intent",
            {"query": test_case["query"]},
            f"Query intent analysis for: {test_case['query']}"
        )
        
        if "error" not in result:
            detected_intent = result.get("intent_type", "").lower()
            expected_intent = test_case["expected_intent"].lower()
            
            if detected_intent == expected_intent:
                print(f"✅ Intent correctly detected: {detected_intent}")
            else:
                print(f"⚠️ Intent mismatch: expected {expected_intent}, got {detected_intent}")
        
        results.append(result)
    
    return results

def test_query_complexity_analysis():
    """Test query complexity analysis."""
    print("\n" + "="*60)
    print("TESTING QUERY COMPLEXITY ANALYSIS")
    print("="*60)
    
    test_queries = [
        "What is a carburetor?",
        "How does the fuel injection system work?",
        "Compare carburetor vs fuel injection systems",
        "What causes engine knocking and how does it affect performance?",
        "Explain the multi-step process of engine combustion"
    ]
    
    results = []
    for query in test_queries:
        result = test_api_endpoint(
            "query-complexity-analysis",
            {"query": query},
            f"Complexity analysis for: {query}"
        )
        results.append(result)
    
    return results

def test_causal_reasoning():
    """Test causal reasoning capabilities."""
    print("\n" + "="*60)
    print("TESTING CAUSAL REASONING")
    print("="*60)
    
    causal_queries = [
        "What causes engine overheating?",
        "How does low oil pressure affect engine performance?",
        "What leads to brake failure?",
        "Why does the transmission slip?",
        "What causes battery drain?"
    ]
    
    results = []
    for query in causal_queries:
        result = test_api_endpoint(
            "causal-reasoning",
            {"query": query},
            f"Causal reasoning for: {query}"
        )
        results.append(result)
    
    return results

def test_comparative_reasoning():
    """Test comparative reasoning capabilities."""
    print("\n" + "="*60)
    print("TESTING COMPARATIVE REASONING")
    print("="*60)
    
    comparative_queries = [
        "Compare electric vs gasoline engines",
        "What are the differences between manual and automatic transmissions?",
        "Compare drum brakes vs disc brakes",
        "What are the advantages of fuel injection over carburetion?",
        "Compare front-wheel drive vs rear-wheel drive"
    ]
    
    results = []
    for query in comparative_queries:
        result = test_api_endpoint(
            "comparative-reasoning",
            {"query": query},
            f"Comparative reasoning for: {query}"
        )
        results.append(result)
    
    return results

def test_multi_hop_reasoning():
    """Test multi-hop reasoning capabilities."""
    print("\n" + "="*60)
    print("TESTING MULTI-HOP REASONING")
    print("="*60)
    
    multi_hop_queries = [
        "How does the fuel system connect to the engine?",
        "What is the relationship between battery and starter motor?",
        "How do brakes connect to the wheel system?",
        "What connects the transmission to the wheels?",
        "How does the cooling system affect engine performance?"
    ]
    
    results = []
    for query in multi_hop_queries:
        result = test_api_endpoint(
            "multi-hop-reasoning",
            {"query": query, "max_hops": 3},
            f"Multi-hop reasoning for: {query}"
        )
        results.append(result)
    
    return results

def test_advanced_reasoning():
    """Test the general advanced reasoning endpoint."""
    print("\n" + "="*60)
    print("TESTING ADVANCED REASONING")
    print("="*60)
    
    advanced_queries = [
        "What is the relationship between engine components?",
        "How does the electrical system work?",
        "What causes common engine problems?",
        "Compare different engine types",
        "Explain the transmission system"
    ]
    
    results = []
    for query in advanced_queries:
        result = test_api_endpoint(
            "advanced-reasoning",
            {"query": query},
            f"Advanced reasoning for: {query}"
        )
        results.append(result)
    
    return results

def test_enhanced_query_processing():
    """Test enhanced query processing with full pipeline."""
    print("\n" + "="*60)
    print("TESTING ENHANCED QUERY PROCESSING")
    print("="*60)
    
    enhanced_queries = [
        "What is the relationship between engine and transmission?",
        "How does low oil pressure cause engine damage?",
        "Compare electric and gasoline engines",
        "What are the steps to replace brake pads?",
        "Analyze the impact of temperature on battery performance"
    ]
    
    results = []
    for query in enhanced_queries:
        result = test_api_endpoint(
            "enhanced-query",
            {"query": query},
            f"Enhanced query processing for: {query}"
        )
        results.append(result)
    
    return results

def generate_test_report(all_results: Dict[str, Any]):
    """Generate a comprehensive test report."""
    print("\n" + "="*60)
    print("TEST REPORT SUMMARY")
    print("="*60)
    
    total_tests = 0
    successful_tests = 0
    failed_tests = 0
    
    for test_name, results in all_results.items():
        print(f"\n📊 {test_name.upper()}:")
        
        if isinstance(results, list):
            test_count = len(results)
            error_count = sum(1 for r in results if "error" in r)
            success_count = test_count - error_count
            
            total_tests += test_count
            successful_tests += success_count
            failed_tests += error_count
            
            print(f"  Tests: {test_count}")
            print(f"  Successful: {success_count}")
            print(f"  Failed: {error_count}")
            print(f"  Success Rate: {(success_count/test_count)*100:.1f}%")
            
            if error_count > 0:
                print("  Errors:")
                for i, result in enumerate(results):
                    if "error" in result:
                        print(f"    {i+1}. {result['error']}")
        else:
            print(f"  Single test result: {'✅ Success' if 'error' not in results else '❌ Failed'}")
            total_tests += 1
            if "error" not in results:
                successful_tests += 1
            else:
                failed_tests += 1
    
    print(f"\n📈 OVERALL SUMMARY:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Successful: {successful_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Overall Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    # Save detailed results
    with open("advanced_reasoning_test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: advanced_reasoning_test_results.json")

def main():
    """Run all advanced reasoning tests."""
    print("🚀 Starting Advanced Reasoning Feature Tests")
    print("="*60)
    
    # Wait for API to be ready
    print("⏳ Waiting for API to be ready...")
    time.sleep(5)
    
    all_results = {}
    
    # Run all test suites
    all_results["query_intent_analysis"] = test_query_intent_analysis()
    all_results["query_complexity_analysis"] = test_query_complexity_analysis()
    all_results["causal_reasoning"] = test_causal_reasoning()
    all_results["comparative_reasoning"] = test_comparative_reasoning()
    all_results["multi_hop_reasoning"] = test_multi_hop_reasoning()
    all_results["advanced_reasoning"] = test_advanced_reasoning()
    all_results["enhanced_query_processing"] = test_enhanced_query_processing()
    
    # Generate report
    generate_test_report(all_results)
    
    print("\n🎉 Advanced reasoning feature tests completed!")

if __name__ == "__main__":
    main() 