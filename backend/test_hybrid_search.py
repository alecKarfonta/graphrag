#!/usr/bin/env python3
"""Test script for hybrid search functionality."""

import os
import tempfile
from hybrid_retriever import HybridRetriever
from query_processor import QueryProcessor
from enhanced_document_processor import EnhancedDocumentProcessor

def create_test_documents():
    """Create test documents for search testing."""
    documents = {}
    
    # Technical document about brake systems
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        Brake System Components and Operation
        
        The brake system consists of several key components that work together to stop the vehicle safely.
        
        Master Cylinder: The master cylinder is the heart of the brake system. It converts mechanical force from the brake pedal into hydraulic pressure. When the driver presses the brake pedal, the master cylinder piston moves forward, creating pressure in the brake lines.
        
        Brake Calipers: The brake calipers are mounted on the wheel assemblies and contain the brake pads. When hydraulic pressure reaches the calipers, they squeeze the brake pads against the brake rotors, creating friction that slows the wheel rotation.
        
        ABS Module: The Anti-lock Braking System (ABS) module monitors wheel speed sensors and prevents wheel lockup during hard braking. It modulates brake pressure to individual wheels, allowing the driver to maintain steering control during emergency stops.
        
        Brake Lines: Steel brake lines carry hydraulic fluid from the master cylinder to the brake calipers. These lines must be properly maintained to prevent fluid leaks that could cause brake failure.
        
        Regular maintenance of the brake system is essential for vehicle safety. Brake pads should be replaced every 50,000 miles, and brake fluid should be changed every 2 years.
        """)
        documents['brake_system'] = f.name
    
    # Engine maintenance document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        Engine Maintenance and Components
        
        The internal combustion engine is a complex system with many interdependent components.
        
        Engine Block: The engine block is the main structure that contains the cylinders, pistons, and crankshaft. It provides the foundation for all other engine components and must be properly maintained to ensure long engine life.
        
        Camshaft: The camshaft controls the opening and closing of the intake and exhaust valves. It is driven by the crankshaft through a timing belt or chain. Proper timing is crucial for engine performance and efficiency.
        
        Crankshaft: The crankshaft converts the linear motion of the pistons into rotational motion that drives the wheels. It is one of the most critical components in the engine and must be precisely balanced.
        
        Timing Belt: The timing belt synchronizes the rotation of the camshaft and crankshaft. If the timing belt fails, the engine can suffer severe damage. Timing belt replacement is typically scheduled at 100,000 miles.
        
        Regular oil changes every 5,000 miles are essential for engine longevity. The oil lubricates moving parts and helps dissipate heat from the engine.
        """)
        documents['engine_maintenance'] = f.name
    
    return documents

def test_query_processing():
    """Test query understanding and processing."""
    print("=== Testing Query Processing ===")
    
    processor = QueryProcessor()
    
    test_queries = [
        "What is the master cylinder?",
        "How does the brake system work?",
        "Compare brake pads and rotors",
        "Explain the engine timing system",
        "What are the maintenance requirements for the engine?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        analysis = processor.get_query_analysis(query)
        
        print(f"  Intent: {analysis['intent'].primary_intent} (confidence: {analysis['intent'].confidence})")
        print(f"  Entities: {[e.name for e in analysis['entities']]}")
        print(f"  Expanded terms: {analysis['expansion'].expanded_terms}")
        print(f"  Reasoning path: {analysis['reasoning_path'].expected_outcome}")

def test_hybrid_search():
    """Test hybrid search functionality."""
    print("\n=== Testing Hybrid Search ===")
    
    # Create test documents
    documents = create_test_documents()
    
    # Initialize components
    processor = EnhancedDocumentProcessor()
    retriever = HybridRetriever()
    
    # Process documents and add to vector store
    all_chunks = []
    for doc_name, doc_path in documents.items():
        print(f"\nProcessing {doc_name}...")
        chunks = processor.process_document_enhanced(doc_path, use_semantic_chunking=True)
        print(f"  Created {len(chunks)} chunks")
        
        # Convert to dict format
        for chunk in chunks:
            chunk_dict = {
                "text": chunk.text,
                "chunk_id": chunk.chunk_id,
                "source_file": chunk.source_file,
                "metadata": chunk.metadata
            }
            all_chunks.append(chunk_dict)
    
    # Add to vector store
    print(f"\nAdding {len(all_chunks)} chunks to vector store...")
    retriever.add_document_chunks(all_chunks)
    
    # Test different search types
    test_queries = [
        "master cylinder",
        "brake system components",
        "engine maintenance",
        "timing belt replacement"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing query: '{query}' ---")
        
        # Vector search
        vector_results = retriever.vector_search(query, top_k=3)
        print(f"Vector search results: {len(vector_results)}")
        for i, result in enumerate(vector_results[:2]):
            print(f"  {i+1}. {result.content[:100]}... (score: {result.score:.3f})")
        
        # Keyword search
        keywords = query.split()
        keyword_results = retriever.keyword_search(query, keywords)
        print(f"Keyword search results: {len(keyword_results)}")
        for i, result in enumerate(keyword_results[:2]):
            print(f"  {i+1}. {result.content[:100]}... (score: {result.score:.3f})")
        
        # Hybrid search
        hybrid_results = retriever.retrieve(query, top_k=5)
        print(f"Hybrid search results: {len(hybrid_results)}")
        for i, result in enumerate(hybrid_results[:2]):
            print(f"  {i+1}. [{result.result_type}] {result.content[:100]}... (score: {result.score:.3f})")
    
    # Clean up test files
    for doc_path in documents.values():
        try:
            os.unlink(doc_path)
        except:
            pass

def test_multi_hop_reasoning():
    """Test multi-hop reasoning for complex queries."""
    print("\n=== Testing Multi-hop Reasoning ===")
    
    retriever = HybridRetriever()
    
    complex_queries = [
        "How do brake components work together to stop the vehicle?",
        "What is the relationship between engine timing and performance?",
        "Explain the maintenance schedule for the entire vehicle"
    ]
    
    for query in complex_queries:
        print(f"\nComplex query: {query}")
        results = retriever.multi_hop_reasoning(query)
        print(f"  Multi-hop results: {len(results)}")
        for i, result in enumerate(results[:2]):
            print(f"  {i+1}. [{result.result_type}] {result.content[:100]}...")

def test_search_analysis():
    """Test search result analysis and ranking."""
    print("\n=== Testing Search Analysis ===")
    
    retriever = HybridRetriever()
    processor = QueryProcessor()
    
    query = "brake system maintenance"
    analysis = processor.get_query_analysis(query)
    
    print(f"Query: {query}")
    print(f"Intent: {analysis['intent'].primary_intent}")
    print(f"Entities: {[e.name for e in analysis['entities']]}")
    print(f"Reasoning type: {analysis['intent'].reasoning_type}")
    
    # Get search results
    results = retriever.retrieve(query, top_k=5)
    
    print(f"\nSearch results ({len(results)} total):")
    for i, result in enumerate(results):
        print(f"  {i+1}. [{result.result_type}] Score: {result.score:.3f}")
        print(f"     Source: {result.source}")
        print(f"     Content: {result.content[:150]}...")
        print()

if __name__ == "__main__":
    print("=== Hybrid Search Test Suite ===\n")
    
    test_query_processing()
    test_hybrid_search()
    test_multi_hop_reasoning()
    test_search_analysis()
    
    print("\n=== Test Suite Complete ===") 