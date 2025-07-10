#!/usr/bin/env python3
"""
Comprehensive Markdown Integration Test
Tests markdown document ingestion and integration with the knowledge graph system.
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_markdown_integration():
    """Test markdown document ingestion and integration."""
    print("🚀 Starting Comprehensive Markdown Integration Test...")
    print("=" * 80)
    
    # Test 1: Basic markdown ingestion
    print("🔍 Test 1: Markdown Document Ingestion")
    try:
        with open("test_document.md", "rb") as f:
            files = {"files": ("test_document.md", f, "text/markdown")}
            response = requests.post(f"{BASE_URL}/ingest-documents", files=files)
        
        if response.status_code == 200:
            result = response.json()
            chunks = result.get("results", {}).get("test_document.md", {}).get("chunks", [])
            entities = result.get("results", {}).get("test_document.md", {}).get("entities", [])
            relationships = result.get("results", {}).get("test_document.md", {}).get("relationships", [])
            # Ensure entities/relationships are lists
            if not isinstance(entities, list):
                entities = []
            if not isinstance(relationships, list):
                relationships = []
            print(f"   ✅ Success - {len(chunks)} chunks created")
            print(f"   ✅ Entities extracted - {len(entities)} entities")
            print(f"   ✅ Relationships extracted - {len(relationships)} relationships")
            
            # Check for markdown-specific features
            markdown_chunks = [c for c in chunks if c.get("metadata", {}).get("file_type") == ".md"]
            if markdown_chunks:
                print(f"   ✅ Markdown file type correctly identified")
            
            # Check for section headers
            sections = [c.get("section_header") for c in chunks if c.get("section_header")]
            if sections:
                print(f"   ✅ Section headers preserved: {len(set(sections))} unique sections")
            
        else:
            print(f"   ❌ Failed - HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    
    # Test 2: Enhanced extraction on markdown content
    print("🔍 Test 2: Enhanced Extraction on Markdown Content")
    try:
        # Test with content from our markdown document
        test_text = "GraphRAG is an advanced document processing system that uses FastAPI, Neo4j, and Qdrant."
        
        response = requests.post(
            f"{BASE_URL}/extract-entities-relations-enhanced",
            data={
                "text": test_text,
                "domain": "technology",
                "use_spanbert": True,
                "use_dependency_parsing": True,
                "use_entity_linking": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            entities = result.get("entities", [])
            relationships = result.get("relationships", [])
            if not isinstance(entities, list):
                entities = []
            if not isinstance(relationships, list):
                relationships = []
            
            print(f"   ✅ Enhanced extraction successful")
            print(f"   ✅ Entities found: {len(entities)}")
            print(f"   ✅ Relationships found: {len(relationships)}")
            
            # Show some entities
            if entities:
                print(f"   📋 Sample entities: {[e.get('text', '') for e in entities[:3]]}")
            
        else:
            print(f"   ❌ Failed - HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    
    # Test 3: Query processing with markdown content
    print("🔍 Test 3: Query Processing with Markdown Content")
    try:
        response = requests.post(
            f"{BASE_URL}/api/enhanced-query",
            params={"query": "What is GraphRAG and what components does it use?"}
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("answer", "")
            confidence = result.get("confidence", 0)
            
            print(f"   ✅ Query processing successful")
            print(f"   ✅ Confidence: {confidence:.2f}")
            print(f"   📋 Answer preview: {answer[:100]}...")
            
        else:
            print(f"   ❌ Failed - HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    
    # Test 4: Knowledge graph statistics
    print("🔍 Test 4: Knowledge Graph Statistics")
    try:
        response = requests.get(f"{BASE_URL}/knowledge-graph/stats")
        if response.status_code == 200:
            result = response.json()
            nodes = result.get("nodes", 0)
            relationships = result.get("edges", 0)
            print(f"   ✅ Knowledge graph accessible")
            print(f"   📊 Nodes: {nodes}")
            print(f"   📊 Relationships: {relationships}")
        else:
            print(f"   ❌ Failed - HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error - {e}")
    print()
    
    # Test 5: Advanced reasoning with markdown content
    print("🔍 Test 5: Advanced Reasoning with Markdown Content")
    try:
        response = requests.post(
            f"{BASE_URL}/api/advanced-reasoning",
            params={"query": "How does GraphRAG process documents?"}
        )
        
        if response.status_code == 200:
            result = response.json()
            reasoning_paths = result.get("reasoning_paths", [])
            
            print(f"   ✅ Advanced reasoning accessible")
            print(f"   📊 Reasoning paths: {len(reasoning_paths)}")
            
        else:
            print(f"   ❌ Failed - HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    
    # Test 6: System health check
    print("🔍 Test 6: System Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status", "unknown")
            
            print(f"   ✅ System health: {status}")
            
            # Check component status
            components = result.get("components", {})
            for component, status in components.items():
                print(f"   📊 {component}: {status}")
            
        else:
            print(f"   ❌ Failed - HTTP {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error - {e}")
    
    print()
    print("=" * 80)
    print("✅ Markdown Integration Test Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_markdown_integration() 