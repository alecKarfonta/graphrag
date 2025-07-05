#!/usr/bin/env python3
"""Test script for the complete Graph RAG pipeline."""

import os
import tempfile
from typing import List, Dict, Any
from document_processor import DocumentProcessor, DocumentChunk
from enhanced_document_processor import EnhancedDocumentProcessor
from entity_extractor import EntityExtractor, Entity, Relationship, ExtractionResult
from entity_resolution import EntityResolver
from knowledge_graph_builder import KnowledgeGraphBuilder

def create_test_documents():
    """Create test documents for different domains."""
    documents = {}
    
    # Technical document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        Technical System Architecture
        
        The brake system consists of several key components:
        - Master cylinder: Controls hydraulic pressure
        - Brake calipers: Apply force to brake pads
        - ABS module: Prevents wheel lockup during braking
        - Brake lines: Transport hydraulic fluid
        
        The master cylinder connects to the brake calipers through brake lines.
        The ABS module monitors wheel speed and modulates brake pressure.
        Brake pads require regular replacement every 50,000 miles.
        """)
        documents['technical'] = f.name
    
    # Automotive document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        Honda Civic Maintenance Guide
        
        Engine Components:
        - Engine block: Contains pistons and cylinders
        - Camshaft: Controls valve timing
        - Crankshaft: Converts piston motion to rotation
        - Timing belt: Synchronizes camshaft and crankshaft
        
        The camshaft connects to the crankshaft via the timing belt.
        Regular oil changes are required every 5,000 miles.
        Timing belt replacement is scheduled at 100,000 miles.
        """)
        documents['automotive'] = f.name
    
    # Medical document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        Diabetes Treatment Protocol
        
        Symptoms:
        - Frequent urination
        - Increased thirst
        - Fatigue
        - Blurred vision
        
        Treatments:
        - Insulin therapy: Regulates blood glucose
        - Metformin: Reduces glucose production
        - Diet modification: Controls carbohydrate intake
        - Exercise: Improves insulin sensitivity
        
        Insulin treats high blood glucose levels.
        Metformin is prescribed for Type 2 diabetes.
        """)
        documents['medical'] = f.name
    
    return documents

def test_document_processing():
    """Test document processing pipeline."""
    print("=== Testing Document Processing ===")
    
    processor = EnhancedDocumentProcessor()
    documents = create_test_documents()
    
    all_chunks = []
    for domain, file_path in documents.items():
        print(f"\nProcessing {domain} document...")
        try:
            chunks = processor.process_document_enhanced(file_path, use_semantic_chunking=True)
            print(f"  - Created {len(chunks)} chunks")
            all_chunks.extend(chunks)
            
            # Show sample chunk
            if chunks:
                sample = chunks[0]
                print(f"  - Sample chunk: {len(sample.text)} chars")
                print(f"    Content type: {sample.metadata.get('content_type', 'unknown')}")
        except Exception as e:
            print(f"  - Error: {e}")
    
    # Clean up
    for file_path in documents.values():
        try:
            os.unlink(file_path)
        except:
            pass
    
    return all_chunks

def test_entity_extraction(chunks: List[DocumentChunk]):
    """Test entity extraction from document chunks."""
    print("\n=== Testing Entity Extraction ===")
    
    # Note: This requires OpenAI API key
    try:
        extractor = EntityExtractor()
        print("Entity extractor initialized successfully")
        
        all_entities = []
        all_relationships = []
        
        for i, chunk in enumerate(chunks[:3]):  # Test first 3 chunks
            print(f"\nExtracting from chunk {i+1}...")
            try:
                # Determine domain based on content
                content_type = chunk.metadata.get('content_type', 'general')
                domain = 'automotive' if 'brake' in chunk.text.lower() or 'engine' in chunk.text.lower() else 'general'
                
                result = extractor.extract_entities_and_relations(chunk.text, domain)
                print(f"  - Extracted {len(result.entities)} entities")
                print(f"  - Extracted {len(result.relationships)} relationships")
                
                all_entities.extend(result.entities)
                all_relationships.extend(result.relationships)
                
                # Show sample entities
                for entity in result.entities[:3]:
                    print(f"    - {entity.name} ({entity.entity_type})")
                    
            except Exception as e:
                print(f"  - Error: {e}")
        
        return all_entities, all_relationships
        
    except Exception as e:
        print(f"Entity extractor initialization failed: {e}")
        print("Using mock entities for demonstration...")
        
        # Create mock entities for demonstration
        mock_entities = [
            Entity("Master cylinder", "COMPONENT", "Controls hydraulic pressure"),
            Entity("Brake calipers", "COMPONENT", "Apply force to brake pads"),
            Entity("ABS module", "COMPONENT", "Prevents wheel lockup"),
            Entity("Engine block", "COMPONENT", "Contains pistons and cylinders"),
            Entity("Camshaft", "COMPONENT", "Controls valve timing"),
            Entity("Insulin therapy", "TREATMENT", "Regulates blood glucose"),
            Entity("Metformin", "MEDICATION", "Reduces glucose production")
        ]
        
        mock_relationships = [
            Relationship("Master cylinder", "Brake calipers", "CONNECTS_TO", "via brake lines"),
            Relationship("ABS module", "Brake calipers", "MONITORS", "wheel speed"),
            Relationship("Camshaft", "Engine block", "PART_OF", "valve system"),
            Relationship("Insulin therapy", "Diabetes", "TREATS", "blood glucose")
        ]
        
        print(f"  - Created {len(mock_entities)} mock entities")
        print(f"  - Created {len(mock_relationships)} mock relationships")
        
        return mock_entities, mock_relationships

def test_entity_resolution(entities: List[Entity]):
    """Test entity resolution and deduplication."""
    print("\n=== Testing Entity Resolution ===")
    
    if not entities:
        print("No entities to resolve")
        return []
    
    resolver = EntityResolver()
    
    print(f"Original entities: {len(entities)}")
    for entity in entities[:5]:  # Show first 5
        print(f"  - {entity.name} ({entity.entity_type})")
    
    try:
        resolved_entities = resolver.resolve_entities(entities)
        print(f"\nResolved entities: {len(resolved_entities)}")
        for entity in resolved_entities[:5]:  # Show first 5
            print(f"  - {entity.name} ({entity.entity_type})")
        
        return resolved_entities
    except Exception as e:
        print(f"Error in entity resolution: {e}")
        return entities

def test_knowledge_graph_construction(entities: List[Entity], relationships: List[Relationship]):
    """Test knowledge graph construction."""
    print("\n=== Testing Knowledge Graph Construction ===")
    
    if not entities:
        print("No entities to build graph from")
        return
    
    builder = KnowledgeGraphBuilder()
    
    try:
        # Add entities and relationships to graph
        builder.add_entities_and_relationships(entities, relationships)
        
        # Get graph statistics
        G = builder.get_networkx_graph()
        print(f"Graph nodes: {G.number_of_nodes()}")
        print(f"Graph edges: {G.number_of_edges()}")
        
        # Detect communities
        communities = builder.detect_communities(method="louvain")
        print(f"Detected {len(communities)} communities")
        
        # Show community structure
        for comm_id, nodes in list(communities.items())[:3]:  # Show first 3
            print(f"  Community {comm_id}: {len(nodes)} nodes")
            if nodes:
                print(f"    Sample nodes: {nodes[:3]}")
        
        # Generate summaries
        for comm_id, nodes in list(communities.items())[:2]:  # Show first 2
            summary = builder.summarize_community(nodes)
            print(f"  Community {comm_id} summary: {summary[:100]}...")
        
        return builder
        
    except Exception as e:
        print(f"Error in graph construction: {e}")
        return None

def test_full_pipeline():
    """Test the complete pipeline end-to-end."""
    print("=== Graph RAG Full Pipeline Test ===\n")
    
    # Step 1: Document Processing
    chunks = test_document_processing()
    
    # Step 2: Entity Extraction
    entities, relationships = test_entity_extraction(chunks)
    
    # Step 3: Entity Resolution
    resolved_entities = test_entity_resolution(entities)
    
    # Step 4: Knowledge Graph Construction
    builder = test_knowledge_graph_construction(resolved_entities, relationships)
    
    print("\n=== Pipeline Test Complete ===")
    print(f"Final results:")
    print(f"  - Processed {len(chunks)} document chunks")
    print(f"  - Extracted {len(entities)} entities")
    print(f"  - Resolved to {len(resolved_entities)} unique entities")
    print(f"  - Created {len(relationships)} relationships")
    if builder:
        G = builder.get_networkx_graph()
        print(f"  - Built graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

if __name__ == "__main__":
    test_full_pipeline() 