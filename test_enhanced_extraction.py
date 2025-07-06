#!/usr/bin/env python3
"""
Test script for Enhanced Entity and Relationship Extraction
Tests SpanBERT, dependency parsing, and entity linking features
"""

import requests
import json
import time
from typing import Dict, Any

# API configuration
BASE_URL = "http://localhost:8000"

def test_extraction_stats():
    """Test the extraction statistics endpoint."""
    print("🔍 Testing extraction statistics...")
    try:
        response = requests.get(f"{BASE_URL}/extraction-stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Extraction stats retrieved:")
            print(f"   Available methods: {data.get('available_methods', [])}")
            print(f"   SpanBERT available: {data.get('spanbert_available', False)}")
            print(f"   Dependency parsing available: {data.get('dependency_available', False)}")
            print(f"   Entity linking available: {data.get('entity_linking_available', False)}")
            return True
        else:
            print(f"❌ Extraction stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Extraction stats error: {e}")
        return False

def test_enhanced_extraction():
    """Test the enhanced extraction endpoint."""
    print("\n🔍 Testing enhanced extraction...")
    
    text = """
    Microsoft Corporation was founded by Bill Gates and Paul Allen on April 4, 1975. 
    The company is headquartered in Redmond, Washington. During his career at Microsoft, 
    Gates served as CEO and chairman. Microsoft acquired LinkedIn in 2016 for $26.2 billion.
    The company also owns GitHub, which it purchased in 2018.
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/extract-entities-relations-enhanced",
            data={
                "text": text,
                "domain": "technology",
                "use_spanbert": "true",
                "use_dependency": "true",
                "use_entity_linking": "true"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enhanced extraction successful:")
            print(f"   Text: {data['text'][:100]}...")
            print(f"   Domain: {data['domain']}")
            print(f"   Entities found: {data['entity_count']}")
            print(f"   Relationships found: {data['relationship_count']}")
            print(f"   Extraction method: {data['extraction_method']}")
            
            # Show extraction metadata
            metadata = data.get('extraction_metadata', {})
            print(f"   Extraction methods used: {metadata.get('extraction_methods', [])}")
            
            # Show sample entities
            print(f"\n   Sample entities:")
            for entity in data['entities'][:5]:
                print(f"     - {entity['name']} ({entity['type']}) - Confidence: {entity['confidence']:.3f}")
                if 'metadata' in entity and 'extraction_method' in entity['metadata']:
                    print(f"       Method: {entity['metadata']['extraction_method']}")
            
            # Show sample relationships
            print(f"\n   Sample relationships:")
            for rel in data['relationships'][:5]:
                print(f"     - {rel['source']} --[{rel['relation_type']}]--> {rel['target']}")
                print(f"       Confidence: {rel['confidence']:.3f}")
                if 'metadata' in rel and 'extraction_method' in rel['metadata']:
                    print(f"       Method: {rel['metadata']['extraction_method']}")
            
            return True
        else:
            print(f"❌ Enhanced extraction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Enhanced extraction error: {e}")
        return False

def test_enhanced_extraction_with_different_methods():
    """Test enhanced extraction with different method combinations."""
    print("\n🔍 Testing enhanced extraction with different methods...")
    
    text = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976.
    The company is based in Cupertino, California. Tim Cook serves as CEO of Apple.
    Apple acquired Beats Electronics in 2014 for $3 billion.
    """
    
    method_combinations = [
        {"use_spanbert": "true", "use_dependency": "false", "use_entity_linking": "false"},
        {"use_spanbert": "false", "use_dependency": "true", "use_entity_linking": "false"},
        {"use_spanbert": "false", "use_dependency": "false", "use_entity_linking": "true"},
        {"use_spanbert": "true", "use_dependency": "true", "use_entity_linking": "true"}
    ]
    
    method_names = [
        "SpanBERT only",
        "Dependency parsing only", 
        "Entity linking only",
        "All methods combined"
    ]
    
    results = []
    
    for i, (methods, name) in enumerate(zip(method_combinations, method_names)):
        try:
            print(f"   Testing {name}...")
            
            response = requests.post(
                f"{BASE_URL}/extract-entities-relations-enhanced",
                data={
                    "text": text,
                    "domain": "technology",
                    **methods
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "method": name,
                    "entities": data['entity_count'],
                    "relationships": data['relationship_count'],
                    "success": True
                })
                print(f"     ✅ {name}: {data['entity_count']} entities, {data['relationship_count']} relationships")
            else:
                results.append({
                    "method": name,
                    "entities": 0,
                    "relationships": 0,
                    "success": False
                })
                print(f"     ❌ {name}: Failed")
                
        except Exception as e:
            results.append({
                "method": name,
                "entities": 0,
                "relationships": 0,
                "success": False
            })
            print(f"     ❌ {name}: Error - {e}")
    
    return results

def test_enhanced_extraction_test_endpoint():
    """Test the enhanced extraction test endpoint."""
    print("\n🔍 Testing enhanced extraction test endpoint...")
    
    text = """
    Tesla, Inc. was founded by Elon Musk, JB Straubel, Martin Eberhard, Marc Tarpenning, and Ian Wright.
    The company is headquartered in Austin, Texas. Tesla manufactures electric vehicles and clean energy products.
    """
    
    try:
        response = requests.post(
            f"{BASE_URL}/test-enhanced-extraction",
            data={
                "text": text,
                "domain": "technology"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enhanced extraction test successful:")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Message: {data.get('message', '')}")
            print(f"   Entities found: {data.get('entities_found', 0)}")
            print(f"   Relationships found: {data.get('relationships_found', 0)}")
            print(f"   Methods used: {data.get('extraction_methods_used', [])}")
            
            # Show sample entities
            print(f"\n   Sample entities:")
            for entity in data.get('sample_entities', []):
                print(f"     - {entity['name']} ({entity['type']}) - Confidence: {entity['confidence']:.3f}")
                print(f"       Method: {entity['extraction_method']}")
            
            # Show sample relationships
            print(f"\n   Sample relationships:")
            for rel in data.get('sample_relationships', []):
                print(f"     - {rel['source']} --[{rel['relation_type']}]--> {rel['target']}")
                print(f"       Confidence: {rel['confidence']:.3f}")
                print(f"       Method: {rel['extraction_method']}")
            
            return True
        else:
            print(f"❌ Enhanced extraction test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Enhanced extraction test error: {e}")
        return False

def main():
    """Run all enhanced extraction tests."""
    print("🚀 Starting Enhanced Entity and Relationship Extraction tests...")
    print("=" * 80)
    
    tests = [
        ("Extraction Statistics", test_extraction_stats),
        ("Enhanced Extraction", test_enhanced_extraction),
        ("Enhanced Extraction Test Endpoint", test_enhanced_extraction_test_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    # Test different method combinations
    print("\n🔍 Testing different extraction method combinations...")
    method_results = test_enhanced_extraction_with_different_methods()
    
    successful_methods = [r for r in method_results if r['success']]
    if successful_methods:
        passed += 1
        print(f"✅ Method combination tests: {len(successful_methods)}/{len(method_results)} successful")
    else:
        print(f"❌ Method combination tests: All failed")
    
    total += 1
    
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enhanced extraction tests passed!")
        print("\n📈 Summary of improvements:")
        print("   ✅ SpanBERT integration for better span-based extraction")
        print("   ✅ Dependency parsing for syntactic relationship extraction")
        print("   ✅ Entity linking to knowledge bases for disambiguation")
        print("   ✅ Multi-method ensemble for improved accuracy")
        print("   ✅ Enhanced API endpoints for testing and monitoring")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    main() 