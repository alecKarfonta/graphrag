#!/usr/bin/env python3
"""
Comprehensive test to measure TwoStageFilter performance improvement.
This script compares retrieval performance with and without filtering.
"""

import requests
import json
import time
from typing import Dict, List, Any

def test_search_with_filtering(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Test search with filtering enabled."""
    try:
        response = requests.post(
            "http://localhost:8000/search",
            data={"query": query, "top_k": top_k},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": str(e)}

def test_search_without_filtering(query: str, top_k: int = 5) -> Dict[str, Any]:
    """Test search without filtering (using vector search directly)."""
    try:
        response = requests.post(
            "http://localhost:8000/search-advanced",
            json={
                "query": query,
                "search_type": "vector",
                "top_k": top_k
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": str(e)}

def analyze_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze search results for quality metrics."""
    if "error" in results:
        return {"error": results["error"]}
    
    search_results = results.get("results", [])
    if not search_results:
        return {"error": "No results found"}
    
    # Calculate quality metrics
    scores = [result.get("score", 0) for result in search_results]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    # Check for filtering metadata
    filtered_count = 0
    confidence_scores = []
    for result in search_results:
        metadata = result.get("metadata", {})
        if "confidence" in metadata:
            filtered_count += 1
            confidence_scores.append(metadata["confidence"])
    
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    return {
        "total_results": len(search_results),
        "filtered_results": filtered_count,
        "avg_score": avg_score,
        "max_score": max_score,
        "min_score": min_score,
        "avg_confidence": avg_confidence,
        "has_filtering": filtered_count > 0,
        "sample_results": [
            {
                "content": result.get("content", "")[:100] + "...",
                "score": result.get("score", 0),
                "confidence": result.get("metadata", {}).get("confidence", "N/A")
            }
            for result in search_results[:3]
        ]
    }

def run_comprehensive_test():
    """Run comprehensive filtering performance test."""
    print("🧪 TwoStageFilter Performance Test")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "What is the engine displacement of the Honda Civic?",
        "How many horsepower does the Toyota Camry have?",
        "What type of transmission does the Ford F-150 use?",
        "What are the brake system components?",
        "How to perform engine maintenance?"
    ]
    
    results_summary = {
        "with_filtering": [],
        "without_filtering": [],
        "improvements": []
    }
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {query} ---")
        
        # Test with filtering
        print("Testing with filtering...")
        start_time = time.time()
        with_filtering = test_search_with_filtering(query)
        with_filtering_time = time.time() - start_time
        
        # Test without filtering
        print("Testing without filtering...")
        start_time = time.time()
        without_filtering = test_search_without_filtering(query)
        without_filtering_time = time.time() - start_time
        
        # Analyze results
        with_analysis = analyze_results(with_filtering)
        without_analysis = analyze_results(without_filtering)
        
        print(f"With filtering: {with_analysis.get('total_results', 0)} results, avg score: {with_analysis.get('avg_score', 0):.3f}")
        print(f"Without filtering: {without_analysis.get('total_results', 0)} results, avg score: {without_analysis.get('avg_score', 0):.3f}")
        
        # Calculate improvements
        if "error" not in with_analysis and "error" not in without_analysis:
            score_improvement = with_analysis.get("avg_score", 0) - without_analysis.get("avg_score", 0)
            time_improvement = without_filtering_time - with_filtering_time
            
            improvement = {
                "query": query,
                "score_improvement": score_improvement,
                "time_improvement": time_improvement,
                "filtering_active": with_analysis.get("has_filtering", False),
                "avg_confidence": with_analysis.get("avg_confidence", 0)
            }
            
            results_summary["improvements"].append(improvement)
            
            print(f"Score improvement: {score_improvement:+.3f}")
            print(f"Time improvement: {time_improvement:+.3f}s")
            print(f"Filtering active: {with_analysis.get('has_filtering', False)}")
            print(f"Average confidence: {with_analysis.get('avg_confidence', 0):.3f}")
        
        results_summary["with_filtering"].append(with_analysis)
        results_summary["without_filtering"].append(without_analysis)
    
    # Calculate overall improvements
    if results_summary["improvements"]:
        avg_score_improvement = sum(imp["score_improvement"] for imp in results_summary["improvements"]) / len(results_summary["improvements"])
        avg_time_improvement = sum(imp["time_improvement"] for imp in results_summary["improvements"]) / len(results_summary["improvements"])
        filtering_active_count = sum(1 for imp in results_summary["improvements"] if imp["filtering_active"])
        avg_confidence = sum(imp["avg_confidence"] for imp in results_summary["improvements"]) / len(results_summary["improvements"])
        
        print(f"\n{'='*60}")
        print("OVERALL RESULTS")
        print(f"{'='*60}")
        print(f"Average score improvement: {avg_score_improvement:+.3f}")
        print(f"Average time improvement: {avg_time_improvement:+.3f}s")
        print(f"Filtering active in {filtering_active_count}/{len(results_summary['improvements'])} tests")
        print(f"Average confidence score: {avg_confidence:.3f}")
        
        if avg_score_improvement > 0:
            print("✅ TwoStageFilter is improving retrieval quality!")
        else:
            print("⚠️ TwoStageFilter may need tuning")
    
    # Save detailed results
    with open("filtering_performance_test_results.json", "w") as f:
        json.dump(results_summary, f, indent=2)
    
    print(f"\nDetailed results saved to: filtering_performance_test_results.json")
    return results_summary

if __name__ == "__main__":
    try:
        results = run_comprehensive_test()
        print("\n✅ Performance test completed successfully!")
    except Exception as e:
        print(f"\n❌ Performance test failed: {e}")
        import traceback
        traceback.print_exc() 