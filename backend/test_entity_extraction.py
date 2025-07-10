#!/usr/bin/env python3
"""
Test script for entity extraction and knowledge graph construction.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from entity_extractor import EntityExtractor
from entity_resolution import EntityResolver
from knowledge_graph_builder import KnowledgeGraphBuilder
from document_processor import DocumentProcessor

def test_entity_extraction():
    """Test entity extraction with Claude."""
    print("🧪 Testing Entity Extraction with Claude...")
    
    # Initialize entity extractor
    try:
        extractor = EntityExtractor()
        print("✅ EntityExtractor initialized successfully")
    except ValueError as e:
        print(f"❌ EntityExtractor initialization failed: {e}")
        print("💡 Please set ANTHROPIC_API_KEY environment variable")
        return False
    
    # Test text
    test_text = """
    The Honda Civic is a compact car manufactured by Honda. The 2020 Honda Civic 
    features a 2.0L naturally aspirated engine with 158 horsepower. The brake system 
    includes anti-lock braking system (ABS) and electronic brake distribution (EBD). 
    Regular maintenance includes oil changes every 5,000 miles and brake pad 
    replacement every 30,000 miles.
    """
    
    print(f"📝 Testing with text: {test_text[:100]}...")
    
    try:
        # Extract entities and relationships
        result = extractor.extract_entities_and_relations(test_text, domain="automotive")
        
        print(f"✅ Extraction completed:")
        print(f"   - Entities found: {len(result.entities)}")
        print(f"   - Relationships found: {len(result.relationships)}")
        print(f"   - Claims found: {len(result.claims)}")
        
        # Display entities
        print("\n📋 Extracted Entities:")
        for entity in result.entities:
            print(f"   - {entity.name} ({entity.entity_type}): {entity.description}")
        
        # Display relationships
        print("\n🔗 Extracted Relationships:")
        for rel in result.relationships:
            print(f"   - {rel.source} --[{rel.relation_type}]--> {rel.target}")
            if rel.context:
                print(f"     Context: {rel.context}")
        
        # Display claims
        print("\n💡 Extracted Claims:")
        for claim in result.claims:
            print(f"   - {claim}")
        
        return result.entities
        
    except Exception as e:
        print(f"❌ Entity extraction failed: {e}")
        return None

def test_entity_resolution(entities: list):
    """Test entity resolution and deduplication."""
    print("\n🧪 Testing Entity Resolution...")
    
    if not entities:
        print("⚠️ No entities to resolve, skipping.")
        return None
        
    resolver = EntityResolver()
    
    try:
        # Resolve entities
        resolved_entities = resolver.resolve_entities(entities)
        
        print(f"✅ Entity resolution completed:")
        print(f"   - Original entities: {len(entities)}")
        print(f"   - Resolved entities: {len(resolved_entities)}")
        
        # Display resolved entities
        print("\n📋 Resolved Entities:")
        for entity in resolved_entities:
            print(f"   - {entity.name} ({entity.entity_type}): {entity.description}")
            if entity.metadata and 'merged_from' in entity.metadata:
                print(f"     Merged from: {', '.join(entity.metadata['merged_from'])}")
        
        return resolved_entities
        
    except Exception as e:
        print(f"❌ Entity resolution failed: {e}")
        return None

def test_knowledge_graph_construction(entities: list, relationships: list):
    """Test knowledge graph construction."""
    print("\n🧪 Testing Knowledge Graph Construction...")
    
    if not entities:
        print("⚠️ No entities to add to graph, skipping.")
        return False
    
    try:
        # Initialize knowledge graph builder
        graph_builder = KnowledgeGraphBuilder()
        
        # Add entities and relationships
        graph_builder.add_entities_and_relationships(entities, relationships)
        
        print("✅ Entities and relationships added to graph")
        
        # Get graph statistics
        stats = graph_builder.get_graph_statistics()
        print(f"📊 Graph Statistics:")
        print(f"   - Nodes: {stats['nodes']}")
        print(f"   - Edges: {stats['edges']}")
        print(f"   - Density: {stats['density']:.3f}")
        
        # Detect communities
        communities = graph_builder.detect_communities()
        print(f"   - Communities detected: {len(communities)}")
        
        # Display communities
        print("\n🏘️  Detected Communities:")
        for community in communities:
            print(f"   - {community.name}: {community.summary}")
            print(f"     Entities: {', '.join(community.entities[:5])}{'...' if len(community.entities) > 5 else ''}")
        
        # Enrich graph
        enriched = graph_builder.enrich_graph("inferred_relationships")
        print(f"   - Inferred relationships: {len(enriched)}")
        
        # Export graph
        graph_json = graph_builder.export_graph("json")
        print(f"   - Graph exported (JSON length: {len(graph_json)} chars)")
        
        # Clean up
        graph_builder.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Knowledge graph construction failed: {e}")
        return False

def test_document_processing():
    """Test document processing pipeline."""
    print("\n🧪 Testing Document Processing...")
    
    # Create a test document
    test_content = """
    Honda Civic Maintenance Guide
    
    The Honda Civic requires regular maintenance to ensure optimal performance.
    
    Engine Maintenance:
    - Oil changes every 5,000 miles
    - Air filter replacement every 15,000 miles
    - Spark plug replacement every 60,000 miles
    
    Brake System:
    - Brake pad inspection every 10,000 miles
    - Brake fluid replacement every 30,000 miles
    - ABS system check during regular service
    
    Transmission:
    - Automatic transmission fluid check every 30,000 miles
    - Manual transmission fluid change every 60,000 miles
    """
    
    # Save test document
    test_file = "test_document.txt"
    with open(test_file, "w") as f:
        f.write(test_content)
    
    try:
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Process document
        chunks = processor.process_document(test_file)
        
        print(f"✅ Document processing completed:")
        print(f"   - Chunks created: {len(chunks)}")
        
        # Display chunks
        print("\n📄 Document Chunks:")
        for i, chunk in enumerate(chunks):
            print(f"   Chunk {i+1}: {chunk.text[:100]}...")
            print(f"     Metadata: {chunk.metadata}")
        
        # Clean up
        os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Graph RAG System Tests")
    print("=" * 50)
    
    # Check environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not set. Some tests may fail.")
        print("💡 Please set your Claude API key in the .env file")
    
    # Run tests
    test_document_processing()
    
    print(f"\n{'='*20} Entity Extraction {'='*20}")
    extracted_entities = test_entity_extraction()
    
    print(f"\n{'='*20} Entity Resolution {'='*20}")
    if extracted_entities:
        resolved_entities = test_entity_resolution(extracted_entities)
    else:
        resolved_entities = None
    
    print(f"\n{'='*20} Knowledge Graph Construction {'='*20}")
    # This part needs the relationships as well, which are not currently passed.
    # For now, we'll use the resolved entities and mock relationships for the graph test.
    if resolved_entities:
        mock_relationships = [
            {"source": "Honda Civic", "target": "Engine", "relation": "CONTAINS", "context": "The Civic contains a 2.0L engine"},
            {"source": "Honda Civic", "target": "Brake System", "relation": "CONTAINS", "context": "The Civic includes ABS and EBD"},
            {"source": "Honda Civic", "target": "Honda", "relation": "MANUFACTURED_BY", "context": "Civic is manufactured by Honda"}
        ]
        test_knowledge_graph_construction(resolved_entities, mock_relationships)
    else:
        print("⚠️ Skipping knowledge graph construction due to previous errors.")
    
    print("\n" + "="*50)
    print("🏁 All tests completed.")

if __name__ == "__main__":
    main() 