#!/usr/bin/env python3

import requests
import json
import time

def test_enhanced_features():
    """Test all the new enhanced features."""
    
    print("🧪 Testing Enhanced GraphRAG Features")
    print("=" * 60)
    
    # Test data
    test_entities = [
        {"name": "Engine", "type": "component", "description": "Internal combustion engine", "confidence": 0.9},
        {"name": "engine", "type": "component", "description": "Motor that converts fuel to motion", "confidence": 0.8},
        {"name": "Fuel Pump", "type": "component", "description": "Pumps fuel to the engine", "confidence": 0.9},
        {"name": "fuel pump", "type": "component", "description": "Component that delivers fuel", "confidence": 0.7},
        {"name": "Tesla", "type": "organisation", "description": "Electric vehicle manufacturer", "confidence": 0.9},
        {"name": "Elon Musk", "type": "person", "description": "CEO of Tesla", "confidence": 0.9},
        {"name": "Battery", "type": "component", "description": "Energy storage device", "confidence": 0.8},
        {"name": "battery", "type": "component", "description": "Power source for electric vehicles", "confidence": 0.7}
    ]
    
    test_relationships = [
        {"source": "Engine", "target": "Fuel Pump", "relation": "requires", "confidence": 0.8, "context": "Engine needs fuel to operate"},
        {"source": "Fuel Pump", "target": "Engine", "relation": "supplies", "confidence": 0.8, "context": "Fuel pump provides fuel to engine"},
        {"source": "Tesla", "target": "Elon Musk", "relation": "employs", "confidence": 0.9, "context": "Elon Musk is CEO of Tesla"},
        {"source": "Elon Musk", "target": "Tesla", "relation": "works for", "confidence": 0.9, "context": "Elon Musk works at Tesla"},
        {"source": "Tesla", "target": "Battery", "relation": "produces", "confidence": 0.8, "context": "Tesla manufactures batteries"},
        {"source": "Battery", "target": "Engine", "relation": "replaces", "confidence": 0.7, "context": "Battery replaces engine in electric vehicles"}
    ]
    
    base_url = "http://localhost:8000"
    
    # Test 1: Entity Linking
    print("\n1️⃣ Testing Entity Linking")
    print("-" * 30)
    
    try:
        response = requests.post(
            f"{base_url}/entity/link",
            json=test_entities,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Entity linking successful")
            print(f"   - Entities processed: {len(result['entities'])}")
            print(f"   - Links created: {len(result['links'])}")
            print(f"   - Clusters found: {len(result['clusters'])}")
            print(f"   - Statistics: {result['statistics']}")
        else:
            print(f"❌ Entity linking failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Entity linking error: {str(e)}")
    
    # Test 2: Entity Disambiguation
    print("\n2️⃣ Testing Entity Disambiguation")
    print("-" * 30)
    
    try:
        entity_to_disambiguate = {"name": "Engine", "type": "component", "description": "Motor component"}
        context = "The engine requires fuel from the fuel pump to operate properly"
        
        response = requests.post(
            f"{base_url}/entity/disambiguate",
            json={
                "entity": entity_to_disambiguate,
                "context": context
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Entity disambiguation successful")
            print(f"   - Original: {result['original_entity']['name']}")
            print(f"   - Disambiguated: {result['disambiguated_entity']['name']}")
            print(f"   - Context: {result['context']}")
        else:
            print(f"❌ Entity disambiguation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Entity disambiguation error: {str(e)}")
    
    # Test 3: Relationship Explanation
    print("\n3️⃣ Testing Relationship Explanation")
    print("-" * 30)
    
    try:
        response = requests.post(
            f"{base_url}/reasoning/explain-relationship",
            json={
                "source": "Engine",
                "target": "Fuel Pump",
                "entities": test_entities,
                "relationships": test_relationships
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Relationship explanation successful")
            print(f"   - Source: {result['source']}")
            print(f"   - Target: {result['target']}")
            print(f"   - Paths found: {len(result['paths'])}")
            print(f"   - Inferred relationships: {len(result['inferred_relationships'])}")
            print(f"   - Explanation: {result['explanation']}")
            print(f"   - Confidence: {result['confidence']}")
        else:
            print(f"❌ Relationship explanation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Relationship explanation error: {str(e)}")
    
    # Test 4: Multi-hop Reasoning
    print("\n4️⃣ Testing Multi-hop Reasoning")
    print("-" * 30)
    
    try:
        response = requests.post(
            f"{base_url}/reasoning/multi-hop",
            json={
                "source": "Engine",
                "target": "Tesla",
                "max_hops": 3,
                "entities": test_entities,
                "relationships": test_relationships
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Multi-hop reasoning successful")
            print(f"   - Source: {result['source']}")
            print(f"   - Target: {result['target']}")
            print(f"   - Max hops: {result['max_hops']}")
            print(f"   - Paths found: {result['path_count']}")
            print(f"   - Inferred relationships: {result['inferred_count']}")
            
            if result['paths']:
                print(f"   - Sample path: {' -> '.join(result['paths'][0]['path'])}")
        else:
            print(f"❌ Multi-hop reasoning failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Multi-hop reasoning error: {str(e)}")
    
    # Test 5: Enhanced Query Processing
    print("\n5️⃣ Testing Enhanced Query Processing")
    print("-" * 30)
    
    try:
        response = requests.post(
            f"{base_url}/query/enhanced",
            json={
                "query": "How is Engine related to Fuel Pump?",
                "search_type": "graph",
                "top_k": 10,
                "domain": "automotive"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Enhanced query processing successful")
            print(f"   - Query: {result['query']}")
            print(f"   - Results: {len(result['results'])}")
            print(f"   - Reasoning paths: {len(result['reasoning_paths'])}")
            print(f"   - Inferred relationships: {len(result['inferred_relationships'])}")
            print(f"   - Entity clusters: {len(result['entity_clusters'])}")
            print(f"   - Explanation: {result['explanation']}")
            print(f"   - Confidence: {result['confidence']}")
        else:
            print(f"❌ Enhanced query processing failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Enhanced query processing error: {str(e)}")
    
    # Test 6: Graph Statistics
    print("\n6️⃣ Testing Graph Statistics")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/reasoning/graph-statistics", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Graph statistics successful")
            print(f"   - Graph stats: {result['graph_statistics']}")
            print(f"   - Entity centrality: {len(result['entity_centrality'])} entities")
            print(f"   - Entity clusters: {result['cluster_count']}")
        else:
            print(f"❌ Graph statistics failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Graph statistics error: {str(e)}")
    
    # Test 7: Query Statistics
    print("\n7️⃣ Testing Query Statistics")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/query/statistics", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query statistics successful")
            print(f"   - Query stats: {result['query_statistics']}")
        else:
            print(f"❌ Query statistics failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Query statistics error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Enhanced Features Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_enhanced_features() 