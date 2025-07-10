#!/usr/bin/env python3
"""
Test script to verify GraphRAG persistent storage functionality
"""

import requests
import time
import json
import subprocess
import os
from datetime import datetime

def test_api_health():
    """Test if all APIs are healthy"""
    print("🔍 Testing API health...")
    
    apis = [
        ("Main API", "http://localhost:8000/health"),
        ("NER API", "http://localhost:8001/health"),
        ("Relationship API", "http://localhost:8002/health")
    ]
    
    for name, url in apis:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Healthy")
            else:
                print(f"❌ {name}: Unhealthy (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Connection failed - {e}")
    
    print()

def test_document_ingestion():
    """Test document ingestion and verify data persistence"""
    print("📄 Testing document ingestion...")
    
    # Test document content
    test_content = """
    Artificial Intelligence and Machine Learning
    
    Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines.
    Machine Learning (ML) is a subset of AI that enables computers to learn and improve from experience.
    
    Key technologies include:
    - Neural Networks
    - Deep Learning
    - Natural Language Processing
    - Computer Vision
    
    Companies like Google, Microsoft, and OpenAI are leading AI research and development.
    """
    
    try:
        # Ingest test document
        response = requests.post(
            "http://localhost:8000/ingest",
            json={
                "content": test_content,
                "metadata": {
                    "title": "AI and ML Overview",
                    "domain": "technology",
                    "source": "test"
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document ingested successfully")
            print(f"   - Entities found: {len(result.get('entities', []))}")
            print(f"   - Relationships found: {len(result.get('relationships', []))}")
            return True
        else:
            print(f"❌ Document ingestion failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Document ingestion error: {e}")
        return False

def test_knowledge_graph_query():
    """Test knowledge graph querying"""
    print("🔍 Testing knowledge graph queries...")
    
    try:
        # Test basic query
        response = requests.post(
            "http://localhost:8000/query",
            json={
                "query": "What is artificial intelligence?",
                "max_results": 5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful")
            print(f"   - Results: {len(result.get('results', []))}")
            return True
        else:
            print(f"❌ Query failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        return False

def test_container_restart():
    """Test data persistence across container restarts"""
    print("🔄 Testing container restart and data persistence...")
    
    # Get initial data
    print("📊 Getting initial data...")
    try:
        response = requests.get("http://localhost:8000/graph/stats", timeout=10)
        if response.status_code == 200:
            initial_stats = response.json()
            print(f"   - Initial entities: {initial_stats.get('entity_count', 0)}")
            print(f"   - Initial relationships: {initial_stats.get('relationship_count', 0)}")
        else:
            print("❌ Failed to get initial stats")
            return False
    except Exception as e:
        print(f"❌ Error getting initial stats: {e}")
        return False
    
    # Restart the API container
    print("🔄 Restarting API container...")
    try:
        subprocess.run(
            ["docker", "compose", "restart", "api"],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ API container restarted")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to restart API container: {e}")
        return False
    
    # Wait for container to be healthy
    print("⏳ Waiting for API to be healthy...")
    max_wait = 60
    wait_time = 0
    
    while wait_time < max_wait:
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is healthy after restart")
                break
        except:
            pass
        
        time.sleep(2)
        wait_time += 2
        print(f"   Waiting... ({wait_time}s)")
    
    if wait_time >= max_wait:
        print("❌ API did not become healthy after restart")
        return False
    
    # Verify data persistence
    print("📊 Verifying data persistence...")
    try:
        response = requests.get("http://localhost:8000/graph/stats", timeout=10)
        if response.status_code == 200:
            final_stats = response.json()
            print(f"   - Final entities: {final_stats.get('entity_count', 0)}")
            print(f"   - Final relationships: {final_stats.get('relationship_count', 0)}")
            
            # Check if data persisted
            if (final_stats.get('entity_count', 0) > 0 and 
                final_stats.get('relationship_count', 0) > 0):
                print("✅ Data persisted successfully across restart")
                return True
            else:
                print("❌ Data was lost during restart")
                return False
        else:
            print("❌ Failed to get final stats")
            return False
    except Exception as e:
        print(f"❌ Error getting final stats: {e}")
        return False

def test_volume_inspection():
    """Test volume inspection and data verification"""
    print("📦 Testing volume inspection...")
    
    volumes = [
        "graphrag_neo4j_data",
        "graphrag_qdrant_data", 
        "graphrag_ner_cache",
        "graphrag_rel_cache"
    ]
    
    for volume in volumes:
        try:
            # Check volume size
            result = subprocess.run(
                ["docker", "run", "--rm", "-v", f"{volume}:/data", "alpine", "du", "-sh", "/data"],
                capture_output=True,
                text=True,
                check=True
            )
            size = result.stdout.strip().split()[0]
            print(f"   - {volume}: {size}")
            
            # Check if volume has data
            if size != "0B" and size != "4.0K":
                print(f"      ✅ {volume} has data")
            else:
                print(f"      ⚠️  {volume} appears empty")
                
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error inspecting {volume}: {e}")
    
    print()

def test_backup_functionality():
    """Test backup and restore functionality"""
    print("💾 Testing backup functionality...")
    
    try:
        # Create a backup
        print("📦 Creating backup...")
        result = subprocess.run(
            ["./scripts/backup.sh"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Backup created successfully")
        
        # List backups
        print("📋 Listing backups...")
        result = subprocess.run(
            ["./scripts/manage_data.sh", "list-backups"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup test failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main test function"""
    print("🚀 GraphRAG Persistent Storage Test")
    print("=" * 50)
    print()
    
    tests = [
        ("API Health Check", test_api_health),
        ("Document Ingestion", test_document_ingestion),
        ("Knowledge Graph Query", test_knowledge_graph_query),
        ("Volume Inspection", test_volume_inspection),
        ("Container Restart Test", test_container_restart),
        ("Backup Functionality", test_backup_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
        
        print()
    
    # Summary
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print()
    print(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Persistent storage is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the persistent storage setup.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 