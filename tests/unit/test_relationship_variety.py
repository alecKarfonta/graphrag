#!/usr/bin/env python3

import requests
import json

def test_relationship_extraction():
    """Test relationship extraction with various text samples to see relationship variety."""
    
    # Test text samples that should trigger different relationship types
    test_samples = [
        {
            "name": "Business relationships",
            "text": "John Smith works for Microsoft Corporation. Microsoft was founded by Bill Gates in 1975. The company is located in Redmond, Washington. Microsoft acquired LinkedIn in 2016. Tesla produces electric vehicles."
        },
        {
            "name": "Technical relationships", 
            "text": "The engine contains the crankshaft. The fuel pump supplies the injectors. The brake system controls the wheels. The alternator connects to the battery. The oil filter replaces the old filter."
        },
        {
            "name": "Maintenance relationships",
            "text": "Oil change procedure maintains the engine. The maintenance is scheduled for every 5000 miles. The repair procedure fixes the transmission problem. The diagnostic tool requires the OBD port."
        },
        {
            "name": "Mixed relationships",
            "text": "Ford Motor Company produces the F-150 truck. The engine contains pistons and cylinders. The maintenance procedure requires special tools. The company is located in Dearborn, Michigan."
        }
    ]
    
    print("🧪 Testing Relationship Extraction Variety")
    print("=" * 50)
    
    for i, sample in enumerate(test_samples, 1):
        print(f"\n📝 Test {i}: {sample['name']}")
        print(f"Text: {sample['text']}")
        
        try:
            # Extract entities and relationships
            response = requests.post(
                "http://localhost:8000/extract-entities-relations",
                json={
                    "text": sample["text"],
                    "domain": "automotive"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                entities = result.get("entities", [])
                relationships = result.get("relationships", [])
                
                print(f"\n✅ Found {len(entities)} entities and {len(relationships)} relationships")
                
                # Show entities
                if entities:
                    print("\n🏷️  Entities:")
                    for entity in entities[:5]:  # Show first 5
                        print(f"  - {entity['name']} ({entity['entity_type']})")
                    if len(entities) > 5:
                        print(f"  ... and {len(entities) - 5} more")
                
                # Show relationships by type
                if relationships:
                    print("\n🔗 Relationships by type:")
                    rel_types = {}
                    for rel in relationships:
                        rel_type = rel.get('relation_type', 'unknown')
                        rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
                    
                    for rel_type, count in sorted(rel_types.items()):
                        print(f"  - {rel_type}: {count}")
                        
                    # Show some example relationships
                    print("\n📋 Example relationships:")
                    for rel in relationships[:3]:  # Show first 3
                        print(f"  - {rel.get('source', 'N/A')} --[{rel.get('relation_type', 'N/A')}]--> {rel.get('target', 'N/A')}")
                    if len(relationships) > 3:
                        print(f"  ... and {len(relationships) - 3} more")
                else:
                    print("❌ No relationships found")
                    
            else:
                print(f"❌ API request failed: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing sample {i}: {e}")
        
        print("-" * 50)
    
    print("\n🎯 Summary: Check if we're getting diverse relationship types beyond just 'part of'")

if __name__ == "__main__":
    test_relationship_extraction() 