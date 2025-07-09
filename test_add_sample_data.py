#!/usr/bin/env python3
"""
Test script to add sample data to the knowledge graph for testing Phase 2 reasoning.

This script will:
1. Add sample entities and relationships to the knowledge graph
2. Test the reasoning endpoints with actual data
3. Verify that the reasoning engine can find paths
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"

def add_sample_entities():
    """Add sample entities to the knowledge graph."""
    print("🔧 Adding sample entities to knowledge graph...")
    
    sample_entities = [
        {
            "name": "Machine Learning",
            "type": "TECHNOLOGY",
            "description": "A subset of artificial intelligence that enables computers to learn from data",
            "properties": {
                "category": "AI",
                "complexity": "high",
                "applications": ["prediction", "classification", "clustering"]
            }
        },
        {
            "name": "Deep Learning",
            "type": "TECHNOLOGY", 
            "description": "A subset of machine learning using neural networks with multiple layers",
            "properties": {
                "category": "AI",
                "complexity": "very_high",
                "applications": ["image_recognition", "natural_language_processing", "speech_recognition"]
            }
        },
        {
            "name": "Artificial Intelligence",
            "type": "TECHNOLOGY",
            "description": "The simulation of human intelligence in machines",
            "properties": {
                "category": "AI",
                "complexity": "very_high",
                "applications": ["automation", "decision_making", "problem_solving"]
            }
        },
        {
            "name": "Neural Networks",
            "type": "TECHNOLOGY",
            "description": "Computing systems inspired by biological neural networks",
            "properties": {
                "category": "AI",
                "complexity": "high",
                "applications": ["pattern_recognition", "data_processing"]
            }
        },
        {
            "name": "Supervised Learning",
            "type": "METHOD",
            "description": "Machine learning approach using labeled training data",
            "properties": {
                "category": "ML_METHOD",
                "complexity": "medium",
                "applications": ["classification", "regression"]
            }
        },
        {
            "name": "Unsupervised Learning",
            "type": "METHOD",
            "description": "Machine learning approach using unlabeled data",
            "properties": {
                "category": "ML_METHOD", 
                "complexity": "medium",
                "applications": ["clustering", "dimensionality_reduction"]
            }
        }
    ]
    
    for entity in sample_entities:
        try:
            response = requests.post(
                f"{BASE_URL}/api/entities",
                json=entity,
                timeout=10
            )
            if response.status_code == 200:
                print(f"  ✅ Added entity: {entity['name']}")
            else:
                print(f"  ❌ Failed to add entity {entity['name']}: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error adding entity {entity['name']}: {e}")

def add_sample_relationships():
    """Add sample relationships to the knowledge graph."""
    print("\n🔗 Adding sample relationships to knowledge graph...")
    
    sample_relationships = [
        {
            "source": "Deep Learning",
            "target": "Machine Learning", 
            "relation": "IS_A",
            "properties": {
                "confidence": 0.95,
                "description": "Deep learning is a subset of machine learning"
            }
        },
        {
            "source": "Machine Learning",
            "target": "Artificial Intelligence",
            "relation": "IS_A", 
            "properties": {
                "confidence": 0.90,
                "description": "Machine learning is a subset of artificial intelligence"
            }
        },
        {
            "source": "Deep Learning",
            "target": "Neural Networks",
            "relation": "USES",
            "properties": {
                "confidence": 0.95,
                "description": "Deep learning uses neural networks as its core technology"
            }
        },
        {
            "source": "Supervised Learning",
            "target": "Machine Learning",
            "relation": "IS_A",
            "properties": {
                "confidence": 0.85,
                "description": "Supervised learning is a method of machine learning"
            }
        },
        {
            "source": "Unsupervised Learning", 
            "target": "Machine Learning",
            "relation": "IS_A",
            "properties": {
                "confidence": 0.85,
                "description": "Unsupervised learning is a method of machine learning"
            }
        },
        {
            "source": "Supervised Learning",
            "target": "Unsupervised Learning",
            "relation": "COMPARES_TO",
            "properties": {
                "confidence": 0.80,
                "description": "Supervised and unsupervised learning are different approaches"
            }
        },
        {
            "source": "Neural Networks",
            "target": "Deep Learning",
            "relation": "ENABLES",
            "properties": {
                "confidence": 0.90,
                "description": "Neural networks enable deep learning capabilities"
            }
        }
    ]
    
    for rel in sample_relationships:
        try:
            response = requests.post(
                f"{BASE_URL}/api/relationships",
                json=rel,
                timeout=10
            )
            if response.status_code == 200:
                print(f"  ✅ Added relationship: {rel['source']} {rel['relation']} {rel['target']}")
            else:
                print(f"  ❌ Failed to add relationship: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Error adding relationship: {e}")

def test_reasoning_with_data():
    """Test the reasoning endpoints with the sample data."""
    print("\n🧪 Testing reasoning endpoints with sample data...")
    
    test_queries = [
        "How does deep learning relate to machine learning?",
        "What is the relationship between AI and machine learning?",
        "Compare supervised and unsupervised learning",
        "How do neural networks connect to deep learning?"
    ]
    
    endpoints = [
        ("advanced-reasoning", "Advanced Reasoning"),
        ("causal-reasoning", "Causal Reasoning"), 
        ("comparative-reasoning", "Comparative Reasoning"),
        ("multi-hop-reasoning", "Multi-hop Reasoning")
    ]
    
    for endpoint, description in endpoints:
        print(f"\n📊 Testing {description}:")
        for query in test_queries:
            try:
                response = requests.post(
                    f"{BASE_URL}/api/{endpoint}",
                    params={"query": query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', '')
                    confidence = result.get('confidence', 0.0)
                    total_paths = result.get('total_paths', 0)
                    
                    print(f"  Query: {query}")
                    print(f"    Answer length: {len(answer)} characters")
                    print(f"    Confidence: {confidence:.3f}")
                    print(f"    Total paths: {total_paths}")
                    
                    if len(answer) > 0 and "No relevant" not in answer:
                        print(f"    ✅ Found reasoning paths!")
                        print(f"    Answer preview: {answer[:100]}...")
                    else:
                        print(f"    ⚠️ No reasoning paths found")
                        
                else:
                    print(f"  ❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Exception: {e}")

def check_graph_stats():
    """Check the current knowledge graph statistics."""
    print("\n📈 Checking knowledge graph statistics...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/graph/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"  Nodes: {stats.get('node_count', 0)}")
            print(f"  Relationships: {stats.get('relationship_count', 0)}")
            print(f"  Entity types: {stats.get('entity_types', [])}")
        else:
            print(f"  ❌ Error getting stats: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Exception getting stats: {e}")

def main():
    """Run the complete test."""
    print("🚀 Starting Phase 2 Data Population Test")
    print("="*60)
    
    # Check initial stats
    check_graph_stats()
    
    # Add sample data
    add_sample_entities()
    add_sample_relationships()
    
    # Check stats after adding data
    check_graph_stats()
    
    # Test reasoning with data
    test_reasoning_with_data()
    
    print("\n✅ Phase 2 Data Population Test Complete!")

if __name__ == "__main__":
    main() 