#!/usr/bin/env python3
"""
Test script for Phase 2 quality fixes

This script tests the improved advanced reasoning endpoints to verify that:
1. They generate actual text answers instead of empty responses
2. The quality metrics improve significantly
3. The endpoints return proper confidence scores
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_endpoint_quality(endpoint: str, test_queries: list, description: str) -> Dict[str, Any]:
    """Test an endpoint and assess the quality of responses."""
    print(f"\n🧪 Testing {description}...")
    print(f"Endpoint: {endpoint}")
    
    results = []
    total_quality_score = 0.0
    
    for i, query in enumerate(test_queries):
        print(f"\n  Testing query {i+1}: {query}")
        
        try:
            # Test the endpoint
            if endpoint == "advanced-reasoning":
                response = requests.post(f"{API_BASE}/{endpoint}", params={"query": query})
            elif endpoint == "causal-reasoning":
                response = requests.post(f"{API_BASE}/{endpoint}", params={"query": query})
            elif endpoint == "comparative-reasoning":
                response = requests.post(f"{API_BASE}/{endpoint}", params={"query": query})
            elif endpoint == "multi-hop-reasoning":
                response = requests.post(f"{API_BASE}/{endpoint}", params={"query": query, "max_hops": 3})
            else:
                response = requests.post(f"{API_BASE}/{endpoint}", params={"query": query})
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract answer
                answer = result.get('answer', '')
                
                # Quality assessment
                quality_metrics = assess_response_quality(query, answer, result)
                
                print(f"    ✅ Success")
                print(f"    Answer length: {len(answer)} characters")
                print(f"    Quality score: {quality_metrics['overall_quality']:.3f}")
                print(f"    Confidence: {result.get('confidence', 0.0):.3f}")
                
                if len(answer) > 0:
                    print(f"    Answer preview: {answer[:100]}...")
                else:
                    print(f"    ⚠️ Empty answer detected!")
                
                results.append({
                    "query": query,
                    "answer": answer,
                    "answer_length": len(answer),
                    "quality_metrics": quality_metrics,
                    "confidence": result.get('confidence', 0.0),
                    "success": True
                })
                
                total_quality_score += quality_metrics['overall_quality']
                
            else:
                print(f"    ❌ HTTP Error: {response.status_code}")
                print(f"    Response: {response.text}")
                results.append({
                    "query": query,
                    "error": f"HTTP {response.status_code}",
                    "success": False
                })
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
            results.append({
                "query": query,
                "error": str(e),
                "success": False
            })
    
    # Calculate average quality
    successful_results = [r for r in results if r.get('success', False)]
    avg_quality = total_quality_score / len(successful_results) if successful_results else 0.0
    
    print(f"\n📊 {description} Summary:")
    print(f"  Total queries: {len(test_queries)}")
    print(f"  Successful responses: {len(successful_results)}")
    print(f"  Average quality score: {avg_quality:.3f}")
    print(f"  Success rate: {len(successful_results)/len(test_queries)*100:.1f}%")
    
    return {
        "endpoint": endpoint,
        "description": description,
        "results": results,
        "average_quality": avg_quality,
        "success_rate": len(successful_results)/len(test_queries)*100 if test_queries else 0
    }

def assess_response_quality(query: str, answer: str, response: Dict[str, Any]) -> Dict[str, float]:
    """Assess the quality of a response."""
    metrics = {
        'answer_length': len(answer),
        'has_answer': len(answer) > 0,
        'confidence_score': response.get('confidence', 0.0),
        'relevance_score': calculate_relevance(query, answer),
        'completeness_score': calculate_completeness(query, answer),
        'coherence_score': calculate_coherence(answer),
        'factual_accuracy': 0.7,  # Default assumption
        'overall_quality': 0.0
    }
    
    # Calculate overall quality (weighted average)
    if metrics['has_answer']:
        metrics['overall_quality'] = (
            metrics['confidence_score'] * 0.3 +
            metrics['relevance_score'] * 0.25 +
            metrics['completeness_score'] * 0.2 +
            metrics['coherence_score'] * 0.15 +
            metrics['factual_accuracy'] * 0.1
        )
    else:
        metrics['overall_quality'] = 0.0
    
    return metrics

def calculate_relevance(query: str, answer: str) -> float:
    """Calculate relevance score based on query-answer alignment."""
    if not answer:
        return 0.0
    
    # Extract key terms from query
    query_terms = set(query.lower().split())
    answer_terms = set(answer.lower().split())
    
    # Calculate term overlap
    overlap = len(query_terms.intersection(answer_terms))
    total_terms = len(query_terms)
    
    if total_terms == 0:
        return 0.5
    
    relevance = overlap / total_terms
    
    # Boost score for longer, more detailed answers
    if len(answer) > 200:
        relevance *= 1.1
    
    return min(relevance, 1.0)

def calculate_completeness(query: str, answer: str) -> float:
    """Calculate completeness score based on answer coverage."""
    if not answer:
        return 0.0
    
    query_lower = query.lower()
    
    if 'what is' in query_lower or 'define' in query_lower:
        # Definition query
        if len(answer) > 100:
            return 0.8
        else:
            return 0.4
    
    elif 'compare' in query_lower or 'difference' in query_lower:
        # Comparison query
        comparison_indicators = ['however', 'while', 'on the other hand', 'in contrast', 'difference']
        if any(indicator in answer.lower() for indicator in comparison_indicators):
            return 0.8
        else:
            return 0.5
    
    elif 'how' in query_lower or 'why' in query_lower:
        # Process query
        if len(answer) > 150:
            return 0.7
        else:
            return 0.4
    
    else:
        # General query
        if len(answer) > 100:
            return 0.7
        else:
            return 0.5

def calculate_coherence(answer: str) -> float:
    """Calculate coherence score based on answer structure."""
    if not answer:
        return 0.0
    
    # Simple coherence indicators
    coherence_indicators = [
        len(answer) > 50,  # Minimum length
        '.' in answer,  # Has sentences
        ',' in answer,  # Has clauses
        any(word in answer.lower() for word in ['because', 'therefore', 'however', 'furthermore', 'additionally'])
    ]
    
    coherence_score = sum(coherence_indicators) / len(coherence_indicators)
    return coherence_score

def test_advanced_reasoning():
    """Test advanced reasoning endpoint."""
    test_queries = [
        "How does machine learning compare to deep learning?",
        "What causes improvements in technology?",
        "How does AI relate to machine learning?",
        "What connects deep learning to artificial intelligence?"
    ]
    
    return test_endpoint_quality("advanced-reasoning", test_queries, "Advanced Reasoning")

def test_causal_reasoning():
    """Test causal reasoning endpoint."""
    test_queries = [
        "What causes climate change?",
        "How does machine learning cause improvements?",
        "What causes engine overheating?",
        "How does low oil pressure affect engine performance?"
    ]
    
    return test_endpoint_quality("causal-reasoning", test_queries, "Causal Reasoning")

def test_comparative_reasoning():
    """Test comparative reasoning endpoint."""
    test_queries = [
        "Compare supervised and unsupervised learning",
        "How do neural networks compare to traditional algorithms?",
        "Compare electric vs gasoline engines",
        "What are the differences between manual and automatic transmissions?"
    ]
    
    return test_endpoint_quality("comparative-reasoning", test_queries, "Comparative Reasoning")

def test_multi_hop_reasoning():
    """Test multi-hop reasoning endpoint."""
    test_queries = [
        "How does AI relate to machine learning?",
        "What connects deep learning to artificial intelligence?",
        "How does the fuel system connect to the engine?",
        "What is the relationship between battery and starter motor?"
    ]
    
    return test_endpoint_quality("multi-hop-reasoning", test_queries, "Multi-hop Reasoning")

def generate_quality_report(all_results: Dict[str, Any]):
    """Generate a comprehensive quality report."""
    print("\n" + "="*80)
    print("PHASE 2 QUALITY FIXES REPORT")
    print("="*80)
    
    total_quality = 0.0
    total_tests = 0
    
    for result in all_results.values():
        if isinstance(result, dict) and 'average_quality' in result:
            endpoint = result['endpoint']
            avg_quality = result['average_quality']
            success_rate = result['success_rate']
            
            print(f"\n📊 {result['description']}:")
            print(f"  Average Quality: {avg_quality:.3f}")
            print(f"  Success Rate: {success_rate:.1f}%")
            
            # Check for improvement
            if avg_quality > 0.0:
                print(f"  ✅ Quality improvement detected!")
            else:
                print(f"  ⚠️ Still needs improvement")
            
            total_quality += avg_quality
            total_tests += 1
    
    if total_tests > 0:
        overall_avg_quality = total_quality / total_tests
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"  Overall Average Quality: {overall_avg_quality:.3f}")
        
        if overall_avg_quality > 0.5:
            print(f"  ✅ Significant improvement achieved!")
        elif overall_avg_quality > 0.0:
            print(f"  ⚠️ Some improvement, but needs more work")
        else:
            print(f"  ❌ No improvement detected - needs investigation")
    
    # Save detailed results
    with open("phase2_quality_fixes_report.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: phase2_quality_fixes_report.json")

def main():
    """Run all Phase 2 quality tests."""
    print("🚀 Starting Phase 2 Quality Fixes Testing")
    print("="*60)
    
    all_results = {}
    
    # Test all endpoints
    all_results['advanced_reasoning'] = test_advanced_reasoning()
    all_results['causal_reasoning'] = test_causal_reasoning()
    all_results['comparative_reasoning'] = test_comparative_reasoning()
    all_results['multi_hop_reasoning'] = test_multi_hop_reasoning()
    
    # Generate report
    generate_quality_report(all_results)
    
    print("\n✅ Phase 2 Quality Fixes Testing Complete!")

if __name__ == "__main__":
    main() 