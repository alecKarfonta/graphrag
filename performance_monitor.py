#!/usr/bin/env python3
"""
Performance monitoring script for the enhanced GraphRAG system.
Tracks response times, success rates, and system health.
"""

import requests
import time
import json
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime

BASE_URL = "http://localhost:8000"

class PerformanceMonitor:
    """Monitor performance of GraphRAG endpoints."""
    
    def __init__(self):
        self.results = {
            'enhanced_query': [],
            'advanced_reasoning': [],
            'causal_reasoning': [],
            'comparative_reasoning': [],
            'multi_hop_reasoning': [],
            'query_complexity': [],
            'query_intent': [],
            'entity_extraction': []
        }
    
    def measure_endpoint(self, endpoint: str, method: str = 'POST', params: Optional[Dict[str, Any]] = None, 
                        json_data: Any = None, expected_status: int = 200) -> Dict[str, Any]:
        """Measure performance of a single endpoint."""
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
            else:
                response = requests.post(f"{BASE_URL}/{endpoint}", params=params, json=json_data)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            success = response.status_code == expected_status
            
            return {
                'endpoint': endpoint,
                'response_time': response_time,
                'status_code': response.status_code,
                'success': success,
                'timestamp': datetime.now().isoformat(),
                'error': None if success else response.text
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'endpoint': endpoint,
                'response_time': end_time - start_time,
                'status_code': None,
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def run_performance_test(self, num_iterations: int = 5):
        """Run comprehensive performance test."""
        print(f"🚀 Running performance test with {num_iterations} iterations per endpoint...")
        
        test_queries = [
            "What is machine learning?",
            "How does deep learning relate to machine learning?",
            "What causes climate change?",
            "Compare supervised and unsupervised learning",
            "How does AI relate to machine learning?"
        ]
        
        test_texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning uses neural networks for complex tasks.",
            "John Smith works at Google in New York."
        ]
        
        for i in range(num_iterations):
            print(f"\n📊 Iteration {i+1}/{num_iterations}")
            
            # Test enhanced query processing
            for query in test_queries[:2]:
                result = self.measure_endpoint('api/enhanced-query', params={'query': query})
                self.results['enhanced_query'].append(result)
            
            # Test advanced reasoning
            result = self.measure_endpoint('api/advanced-reasoning', params={'query': test_queries[1]})
            self.results['advanced_reasoning'].append(result)
            
            # Test causal reasoning
            result = self.measure_endpoint('api/causal-reasoning', params={'query': test_queries[2]})
            self.results['causal_reasoning'].append(result)
            
            # Test comparative reasoning
            result = self.measure_endpoint('api/comparative-reasoning', params={'query': test_queries[3]})
            self.results['comparative_reasoning'].append(result)
            
            # Test multi-hop reasoning
            result = self.measure_endpoint('api/multi-hop-reasoning', params={'query': test_queries[4]})
            self.results['multi_hop_reasoning'].append(result)
            
            # Test query complexity
            result = self.measure_endpoint('api/query-complexity-analysis', params={'query': test_queries[0]})
            self.results['query_complexity'].append(result)
            
            # Test query intent
            result = self.measure_endpoint('api/analyze-query-intent', params={'query': test_queries[1]})
            self.results['query_intent'].append(result)
            
            # Test entity extraction
            for text in test_texts:
                result = self.measure_endpoint('extract-entities-relations', 
                                            json_data={'text': text, 'domain': 'technology'})
                self.results['entity_extraction'].append(result)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            'summary': {},
            'endpoint_details': {},
            'recommendations': []
        }
        
        for endpoint, results in self.results.items():
            if not results:
                continue
                
            # Calculate statistics
            response_times = [r['response_time'] for r in results if r['success']]
            success_count = sum(1 for r in results if r['success'])
            total_count = len(results)
            
            endpoint_stats = {
                'total_requests': total_count,
                'successful_requests': success_count,
                'success_rate': (success_count / total_count * 100) if total_count > 0 else 0,
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'min_response_time': min(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0,
                'median_response_time': statistics.median(response_times) if response_times else 0
            }
            
            report['endpoint_details'][endpoint] = endpoint_stats
        
        # Overall summary
        all_response_times = []
        total_requests = 0
        total_successes = 0
        
        for endpoint_stats in report['endpoint_details'].values():
            all_response_times.extend([endpoint_stats['avg_response_time']] * endpoint_stats['successful_requests'])
            total_requests += endpoint_stats['total_requests']
            total_successes += endpoint_stats['successful_requests']
        
        report['summary'] = {
            'total_requests': total_requests,
            'total_successes': total_successes,
            'overall_success_rate': (total_successes / total_requests * 100) if total_requests > 0 else 0,
            'avg_response_time': statistics.mean(all_response_times) if all_response_times else 0,
            'fastest_endpoint': min(report['endpoint_details'].items(), 
                                  key=lambda x: x[1]['avg_response_time'])[0] if report['endpoint_details'] else None,
            'slowest_endpoint': max(report['endpoint_details'].items(), 
                                  key=lambda x: x[1]['avg_response_time'])[0] if report['endpoint_details'] else None
        }
        
        # Generate recommendations
        for endpoint, stats in report['endpoint_details'].items():
            if stats['success_rate'] < 95:
                report['recommendations'].append(f"⚠️ {endpoint}: Low success rate ({stats['success_rate']:.1f}%)")
            
            if stats['avg_response_time'] > 5.0:
                report['recommendations'].append(f"🐌 {endpoint}: Slow response time ({stats['avg_response_time']:.2f}s)")
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted performance report."""
        print("\n" + "="*60)
        print("📊 PERFORMANCE MONITORING REPORT")
        print("="*60)
        
        # Summary
        summary = report['summary']
        print(f"\n📈 OVERALL SUMMARY:")
        print(f"   Total Requests: {summary['total_requests']}")
        print(f"   Success Rate: {summary['overall_success_rate']:.1f}%")
        print(f"   Average Response Time: {summary['avg_response_time']:.2f}s")
        print(f"   Fastest Endpoint: {summary['fastest_endpoint']}")
        print(f"   Slowest Endpoint: {summary['slowest_endpoint']}")
        
        # Endpoint details
        print(f"\n🔍 ENDPOINT DETAILS:")
        for endpoint, stats in report['endpoint_details'].items():
            print(f"\n   {endpoint.upper()}:")
            print(f"     Success Rate: {stats['success_rate']:.1f}%")
            print(f"     Avg Response Time: {stats['avg_response_time']:.2f}s")
            print(f"     Min/Max Response Time: {stats['min_response_time']:.2f}s / {stats['max_response_time']:.2f}s")
        
        # Recommendations
        if report['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        else:
            print(f"\n✅ All endpoints performing well!")
        
        print("\n" + "="*60)

def main():
    """Run performance monitoring."""
    monitor = PerformanceMonitor()
    monitor.run_performance_test(num_iterations=3)
    report = monitor.generate_report()
    monitor.print_report(report)
    
    # Save report to file
    with open('performance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n💾 Performance report saved to: performance_report.json")

if __name__ == "__main__":
    main() 