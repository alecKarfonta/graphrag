#!/usr/bin/env python3
"""
Test script for the TwoStageFilter system.
This script verifies that the filtering system can be imported and used correctly.
"""

import sys
import os

# Add the graphrag directory to the path
graphrag_path = os.path.join(os.path.dirname(__file__), '..', 'graphrag')
if graphrag_path not in sys.path:
    sys.path.append(graphrag_path)

def test_filtering_import():
    """Test that the filtering system can be imported."""
    try:
        from retrieval.filtering import TwoStageFilter, RetrievedChunk, FilteringResult
        print("✅ Successfully imported TwoStageFilter components")
        return True
    except ImportError as e:
        print(f"❌ Failed to import TwoStageFilter: {e}")
        return False

def test_filtering_initialization():
    """Test that the filtering system can be initialized."""
    try:
        from retrieval.filtering import TwoStageFilter
        
        # Test initialization with different parameters
        filter_system = TwoStageFilter(
            relevance_threshold=0.3,
            quality_threshold=0.5,
            confidence_threshold=0.6,
            max_chunks=10
        )
        print("✅ Successfully initialized TwoStageFilter")
        return filter_system
    except Exception as e:
        print(f"❌ Failed to initialize TwoStageFilter: {e}")
        return None

def test_filtering_functionality():
    """Test the filtering functionality with sample data."""
    try:
        from retrieval.filtering import TwoStageFilter, RetrievedChunk
        
        # Initialize filter
        filter_system = TwoStageFilter(
            relevance_threshold=0.3,
            quality_threshold=0.5,
            confidence_threshold=0.6,
            max_chunks=5
        )
        
        # Create sample retrieved chunks
        sample_chunks = [
            RetrievedChunk(
                content="The Honda Civic has a 1.5L turbocharged engine that produces 180 horsepower. The brake system includes ABS and electronic brake distribution.",
                score=0.8,
                source="honda_manual.txt",
                entity_matches=["Honda Civic", "engine", "horsepower"]
            ),
            RetrievedChunk(
                content="Maybe the car has some engine or something like that.",
                score=0.4,
                source="uncertain_info.txt",
                entity_matches=["car"]
            ),
            RetrievedChunk(
                content="The Toyota Camry features a 2.5L four-cylinder engine with 203 horsepower. The transmission is an 8-speed automatic with manual mode.",
                score=0.9,
                source="toyota_manual.txt",
                entity_matches=["Toyota Camry", "engine", "horsepower", "transmission"]
            )
        ]
        
        # Test filtering
        query = "What is the engine displacement of the Honda Civic?"
        entities = ["Honda Civic", "engine", "displacement"]
        
        result = filter_system.filter_chunks(query, sample_chunks, entities)
        
        print(f"✅ Filtering test completed:")
        print(f"   Original chunks: {len(sample_chunks)}")
        print(f"   Filtered chunks: {len(result.filtered_chunks)}")
        print(f"   Average confidence: {sum(result.confidence_scores) / len(result.confidence_scores) if result.confidence_scores else 0:.3f}")
        print(f"   Filtering metadata: {result.filtering_metadata}")
        
        return True
        
    except Exception as e:
        print(f"❌ Filtering functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all filtering tests."""
    print("🧪 Testing TwoStageFilter System")
    print("=" * 50)
    
    # Test 1: Import
    if not test_filtering_import():
        return False
    
    # Test 2: Initialization
    filter_system = test_filtering_initialization()
    if not filter_system:
        return False
    
    # Test 3: Functionality
    if not test_filtering_functionality():
        return False
    
    print("\n✅ All filtering tests passed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 