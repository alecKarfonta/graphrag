#!/usr/bin/env python3
"""
Quality metrics and validation system for the enhanced GraphRAG system.
Implements confidence scoring, answer validation, and quality assessment.
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

BASE_URL = "http://localhost:8000"

@dataclass
class QualityMetrics:
    """Quality metrics for query responses."""
    confidence_score: float
    relevance_score: float
    completeness_score: float
    coherence_score: float
    factual_accuracy: float
    overall_quality: float
    validation_passed: bool
    issues: List[str]

@dataclass
class ValidationResult:
    """Result of answer validation."""
    is_valid: bool
    confidence: float
    issues: List[str]
    suggestions: List[str]
    metrics: QualityMetrics

class QualityAssessor:
    """Assess quality of GraphRAG responses."""
    
    def __init__(self):
        self.quality_thresholds = {
            'confidence': 0.7,
            'relevance': 0.6,
            'completeness': 0.5,
            'coherence': 0.6,
            'factual_accuracy': 0.8
        }
        
        self.validation_rules = {
            'min_answer_length': 50,
            'max_answer_length': 5000,
            'required_sections': ['introduction', 'explanation'],
            'forbidden_patterns': [
                r'I don\'t know',
                r'I cannot answer',
                r'No information available',
                r'Unable to provide'
            ]
        }
    
    def assess_response_quality(self, query: str, response: Dict[str, Any]) -> QualityMetrics:
        """Assess the quality of a response."""
        issues = []
        
        # Extract response components
        answer = response.get('answer', '')
        confidence = response.get('confidence', 0.0)
        sources = response.get('sources', [])
        reasoning_paths = response.get('reasoning_paths', [])
        
        # Calculate individual scores
        confidence_score = self._calculate_confidence_score(response)
        relevance_score = self._calculate_relevance_score(query, answer)
        completeness_score = self._calculate_completeness_score(query, answer, sources)
        coherence_score = self._calculate_coherence_score(answer)
        factual_accuracy = self._calculate_factual_accuracy(answer)
        
        # Overall quality score (weighted average)
        overall_quality = (
            confidence_score * 0.3 +
            relevance_score * 0.25 +
            completeness_score * 0.2 +
            coherence_score * 0.15 +
            factual_accuracy * 0.1
        )
        
        # Identify issues
        if confidence_score < self.quality_thresholds['confidence']:
            issues.append(f"Low confidence score: {confidence_score:.2f}")
        
        if relevance_score < self.quality_thresholds['relevance']:
            issues.append(f"Low relevance score: {relevance_score:.2f}")
        
        if completeness_score < self.quality_thresholds['completeness']:
            issues.append(f"Low completeness score: {completeness_score:.2f}")
        
        if coherence_score < self.quality_thresholds['coherence']:
            issues.append(f"Low coherence score: {coherence_score:.2f}")
        
        if factual_accuracy < self.quality_thresholds['factual_accuracy']:
            issues.append(f"Low factual accuracy: {factual_accuracy:.2f}")
        
        # Check for forbidden patterns
        for pattern in self.validation_rules['forbidden_patterns']:
            if re.search(pattern, answer, re.IGNORECASE):
                issues.append(f"Contains forbidden pattern: {pattern}")
        
        # Check answer length
        if len(answer) < self.validation_rules['min_answer_length']:
            issues.append(f"Answer too short: {len(answer)} characters")
        
        if len(answer) > self.validation_rules['max_answer_length']:
            issues.append(f"Answer too long: {len(answer)} characters")
        
        validation_passed = len(issues) == 0 and overall_quality >= 0.7
        
        return QualityMetrics(
            confidence_score=confidence_score,
            relevance_score=relevance_score,
            completeness_score=completeness_score,
            coherence_score=coherence_score,
            factual_accuracy=factual_accuracy,
            overall_quality=overall_quality,
            validation_passed=validation_passed,
            issues=issues
        )
    
    def _calculate_confidence_score(self, response: Dict[str, Any]) -> float:
        """Calculate confidence score based on response components."""
        base_confidence = response.get('confidence', 0.0)
        
        # Boost confidence based on reasoning paths
        reasoning_paths = response.get('reasoning_paths', [])
        if reasoning_paths:
            path_confidences = [path.get('confidence', 0.0) for path in reasoning_paths]
            reasoning_confidence = sum(path_confidences) / len(path_confidences)
            base_confidence = (base_confidence + reasoning_confidence) / 2
        
        # Boost confidence based on search strategy
        search_strategy = response.get('search_strategy', {})
        strategy_confidence = search_strategy.get('confidence', 0.0)
        base_confidence = (base_confidence + strategy_confidence) / 2
        
        return min(base_confidence, 1.0)
    
    def _calculate_relevance_score(self, query: str, answer: str) -> float:
        """Calculate relevance score based on query-answer alignment."""
        if not answer:
            return 0.0
        
        # Extract key terms from query
        query_terms = set(re.findall(r'\b\w+\b', query.lower()))
        answer_terms = set(re.findall(r'\b\w+\b', answer.lower()))
        
        # Calculate term overlap
        overlap = len(query_terms.intersection(answer_terms))
        total_terms = len(query_terms)
        
        if total_terms == 0:
            return 0.5  # Neutral score for empty queries
        
        relevance = overlap / total_terms
        
        # Boost score for longer, more detailed answers
        if len(answer) > 200:
            relevance *= 1.1
        
        return min(relevance, 1.0)
    
    def _calculate_completeness_score(self, query: str, answer: str, sources: List[Dict]) -> float:
        """Calculate completeness score based on answer coverage."""
        if not answer:
            return 0.0
        
        # Check if answer addresses the query type
        query_lower = query.lower()
        
        if 'what is' in query_lower or 'define' in query_lower:
            # Definition query - should have clear explanation
            if len(answer) > 100 and any(word in answer.lower() for word in ['is', 'are', 'refers to', 'means']):
                return 0.8
            else:
                return 0.4
        
        elif 'compare' in query_lower or 'difference' in query_lower:
            # Comparison query - should have multiple points
            comparison_indicators = ['however', 'while', 'on the other hand', 'in contrast', 'difference']
            if any(indicator in answer.lower() for indicator in comparison_indicators):
                return 0.8
            else:
                return 0.5
        
        elif 'how' in query_lower or 'why' in query_lower:
            # Process query - should have steps or explanation
            if len(answer) > 150:
                return 0.7
            else:
                return 0.4
        
        # Default completeness score
        return 0.6
    
    def _calculate_coherence_score(self, answer: str) -> float:
        """Calculate coherence score based on answer structure."""
        if not answer:
            return 0.0
        
        # Check for logical structure
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 2:
            return 0.3  # Single sentence answers are less coherent
        
        # Check for transition words
        transition_words = ['however', 'therefore', 'moreover', 'furthermore', 'in addition', 'consequently']
        transitions = sum(1 for word in transition_words if word in answer.lower())
        
        # Check for paragraph structure
        paragraphs = answer.split('\n\n')
        paragraph_score = min(len(paragraphs) / 3, 1.0)  # Normalize to 0-1
        
        # Calculate coherence
        coherence = 0.5  # Base score
        coherence += transitions * 0.1  # Boost for transitions
        coherence += paragraph_score * 0.2  # Boost for structure
        coherence += min(len(sentences) / 5, 0.3)  # Boost for length
        
        return min(coherence, 1.0)
    
    def _calculate_factual_accuracy(self, answer: str) -> float:
        """Calculate factual accuracy score based on answer content."""
        if not answer:
            return 0.0
        
        # Check for factual indicators
        factual_indicators = [
            'research shows', 'studies indicate', 'evidence suggests',
            'according to', 'based on', 'data shows', 'statistics'
        ]
        
        factual_count = sum(1 for indicator in factual_indicators if indicator in answer.lower())
        
        # Check for hedging language (reduces accuracy)
        hedging_words = ['might', 'could', 'possibly', 'perhaps', 'maybe', 'seems']
        hedging_count = sum(1 for word in hedging_words if word in answer.lower())
        
        # Calculate accuracy score
        accuracy = 0.7  # Base score
        accuracy += factual_count * 0.05  # Boost for factual language
        accuracy -= hedging_count * 0.02  # Penalty for hedging
        
        return max(0.0, min(accuracy, 1.0))
    
    def validate_answer(self, query: str, response: Dict[str, Any]) -> ValidationResult:
        """Validate an answer against quality standards."""
        metrics = self.assess_response_quality(query, response)
        
        suggestions = []
        
        if metrics.confidence_score < 0.7:
            suggestions.append("Consider adding more specific information to increase confidence")
        
        if metrics.relevance_score < 0.6:
            suggestions.append("Ensure the answer directly addresses the query terms")
        
        if metrics.completeness_score < 0.5:
            suggestions.append("Provide more comprehensive coverage of the topic")
        
        if metrics.coherence_score < 0.6:
            suggestions.append("Improve answer structure with better transitions and organization")
        
        if len(metrics.issues) > 0:
            suggestions.append("Address the identified quality issues")
        
        return ValidationResult(
            is_valid=metrics.validation_passed,
            confidence=metrics.overall_quality,
            issues=metrics.issues,
            suggestions=suggestions,
            metrics=metrics
        )

class QualityMonitor:
    """Monitor and track quality metrics over time."""
    
    def __init__(self):
        self.assessor = QualityAssessor()
        self.quality_history = []
    
    def test_endpoint_quality(self, endpoint: str, test_queries: List[str]) -> Dict[str, Any]:
        """Test quality of a specific endpoint."""
        print(f"🔍 Testing quality for endpoint: {endpoint}")
        
        results = []
        total_quality = 0.0
        
        for query in test_queries:
            try:
                # Make request to endpoint
                if endpoint == 'enhanced-query':
                    response = requests.post(f"{BASE_URL}/api/{endpoint}", params={'query': query})
                else:
                    response = requests.post(f"{BASE_URL}/api/{endpoint}", params={'query': query})
                
                if response.status_code == 200:
                    result_data = response.json()
                    validation = self.assessor.validate_answer(query, result_data)
                    
                    results.append({
                        'query': query,
                        'validation': validation,
                        'response_time': response.elapsed.total_seconds()
                    })
                    
                    total_quality += validation.confidence
                else:
                    results.append({
                        'query': query,
                        'validation': None,
                        'error': f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                results.append({
                    'query': query,
                    'validation': None,
                    'error': str(e)
                })
        
        avg_quality = total_quality / len(results) if results else 0.0
        
        return {
            'endpoint': endpoint,
            'test_queries': len(test_queries),
            'successful_requests': len([r for r in results if r['validation']]),
            'average_quality': avg_quality,
            'results': results
        }
    
    def run_comprehensive_quality_test(self):
        """Run comprehensive quality test across all endpoints."""
        print("🚀 Running comprehensive quality assessment...")
        
        test_queries = {
            'enhanced-query': [
                "What is machine learning?",
                "How does deep learning relate to machine learning?",
                "What is the difference between supervised and unsupervised learning?"
            ],
            'advanced-reasoning': [
                "How does machine learning compare to deep learning?",
                "What causes improvements in technology?"
            ],
            'causal-reasoning': [
                "What causes climate change?",
                "How does machine learning cause improvements?"
            ],
            'comparative-reasoning': [
                "Compare supervised and unsupervised learning",
                "How do neural networks compare to traditional algorithms?"
            ],
            'multi-hop-reasoning': [
                "How does AI relate to machine learning?",
                "What connects deep learning to artificial intelligence?"
            ]
        }
        
        results = {}
        
        for endpoint, queries in test_queries.items():
            result = self.test_endpoint_quality(endpoint, queries)
            results[endpoint] = result
            
            print(f"\n📊 {endpoint.upper()}:")
            print(f"   Average Quality: {result['average_quality']:.2f}")
            print(f"   Success Rate: {result['successful_requests']}/{result['test_queries']}")
        
        # Generate quality report
        self._generate_quality_report(results)
        
        return results
    
    def _generate_quality_report(self, results: Dict[str, Any]):
        """Generate comprehensive quality report."""
        print("\n" + "="*60)
        print("📊 QUALITY ASSESSMENT REPORT")
        print("="*60)
        
        overall_quality = 0.0
        total_endpoints = 0
        
        for endpoint, result in results.items():
            if result['successful_requests'] > 0:
                overall_quality += result['average_quality']
                total_endpoints += 1
                
                print(f"\n🔍 {endpoint.upper()}:")
                print(f"   Average Quality: {result['average_quality']:.2f}")
                print(f"   Success Rate: {result['successful_requests']}/{result['test_queries']}")
                
                # Show validation issues for first result
                if result['results'] and result['results'][0]['validation']:
                    validation = result['results'][0]['validation']
                    if validation.issues:
                        print(f"   Issues: {', '.join(validation.issues[:2])}")
        
        if total_endpoints > 0:
            overall_avg = overall_quality / total_endpoints
            print(f"\n📈 OVERALL QUALITY: {overall_avg:.2f}")
            
            if overall_avg >= 0.8:
                print("✅ Excellent quality across all endpoints!")
            elif overall_avg >= 0.6:
                print("⚠️ Good quality with room for improvement")
            else:
                print("❌ Quality needs significant improvement")
        
        print("\n" + "="*60)

def main():
    """Run quality assessment."""
    monitor = QualityMonitor()
    results = monitor.run_comprehensive_quality_test()
    
    # Save results
    with open('quality_report.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Quality report saved to: quality_report.json")

if __name__ == "__main__":
    main() 