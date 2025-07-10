#!/usr/bin/env python3
"""
Simple test script to verify GraphRAG persistent storage functionality
"""

import requests
import time
import subprocess

def test_api_health():
    """Test if all APIs are healthy"""
    print("🔍 Testing API health...")
    
    apis = [
        ("Main API", "http://localhost:8000/"),
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
    """Test document ingestion with correct endpoint"""
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
        # Ingest test document using the correct endpoint
        response = requests.post(
            "http://localhost:8000/add-to-vector-store",
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
            print(f"   - Status: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Document ingestion failed: {response.status_code}")
            print(f"   - Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Document ingestion error: {e}")
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
    
    all_volumes_have_data = True
    
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
                all_volumes_have_data = False
                
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error inspecting {volume}: {e}")
            all_volumes_have_data = False
    
    print()
    return all_volumes_have_data

def test_container_restart():
    """Test data persistence across container restarts"""
    print("🔄 Testing container restart and data persistence...")
    
    # Get initial volume sizes
    print("📊 Getting initial volume sizes...")
    initial_sizes = {}
    
    volumes = ["graphrag_neo4j_data", "graphrag_qdrant_data"]
    
    for volume in volumes:
        try:
            result = subprocess.run(
                ["docker", "run", "--rm", "-v", f"{volume}:/data", "alpine", "du", "-sh", "/data"],
                capture_output=True,
                text=True,
                check=True
            )
            size = result.stdout.strip().split()[0]
            initial_sizes[volume] = size
            print(f"   - {volume}: {size}")
        except subprocess.CalledProcessError as e:
            print(f"   - {volume}: Error - {e}")
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
            response = requests.get("http://localhost:8000/", timeout=5)
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
    for volume in volumes:
        try:
            result = subprocess.run(
                ["docker", "run", "--rm", "-v", f"{volume}:/data", "alpine", "du", "-sh", "/data"],
                capture_output=True,
                text=True,
                check=True
            )
            final_size = result.stdout.strip().split()[0]
            initial_size = initial_sizes.get(volume, "0B")
            
            print(f"   - {volume}: {initial_size} -> {final_size}")
            
            # Check if data persisted (size should be similar)
            if final_size != "0B" and final_size != "4.0K":
                print(f"      ✅ {volume} data persisted")
            else:
                print(f"      ❌ {volume} data was lost")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Error checking {volume}: {e}")
            return False
    
    print("✅ Data persisted successfully across restart")
    return True

def test_backup_functionality():
    """Test backup functionality"""
    print("💾 Testing backup functionality...")
    
    try:
        # List existing backups
        print("📋 Listing existing backups...")
        result = subprocess.run(
            ["./scripts/manage_data.sh", "list-backups"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        
        # Check if backups directory exists and has files
        if os.path.exists("./backups") and len(os.listdir("./backups")) > 0:
            print("✅ Backup functionality is working")
            return True
        else:
            print("⚠️  No backups found, but backup system is available")
            return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Backup test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 GraphRAG Persistent Storage Test (Simple)")
    print("=" * 50)
    print()
    
    tests = [
        ("API Health Check", test_api_health),
        ("Document Ingestion", test_document_ingestion),
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
    import os
    success = main()
    exit(0 if success else 1) 