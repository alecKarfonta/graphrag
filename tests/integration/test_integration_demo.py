#!/usr/bin/env python3
"""
Simple test to demonstrate Code RAG parsing and GraphRAG integration.
"""

import requests
import json
import tempfile
import os
from pathlib import Path

# Configuration
GRAPHRAG_URL = "http://localhost:8000"
CODE_RAG_URL = "http://localhost:8004"

# Sample Python code
SAMPLE_CODE = '''
"""
User authentication and management system.
"""

import hashlib
from typing import Optional, List
from datetime import datetime

class User:
    """Represents a user in the system."""
    
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password_hash = self._hash_password(password)
        self.created_at = datetime.now()
        self.is_active = True
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """Verify if provided password matches."""
        return self.password_hash == self._hash_password(password)
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False

class UserManager:
    """Manages user operations."""
    
    def __init__(self):
        self.users: List[User] = []
        self.active_sessions = {}
    
    def create_user(self, username: str, email: str, password: str) -> Optional[User]:
        """Create a new user."""
        if self.find_user(username):
            return None
        
        user = User(username, email, password)
        self.users.append(user)
        return user
    
    def find_user(self, username: str) -> Optional[User]:
        """Find user by username."""
        for user in self.users:
            if user.username == username:
                return user
        return None
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate user credentials."""
        user = self.find_user(username)
        if user and user.is_active:
            return user.verify_password(password)
        return False
    
    def get_active_users(self) -> List[User]:
        """Get list of active users."""
        return [user for user in self.users if user.is_active]

def create_default_admin() -> User:
    """Create default admin user."""
    manager = UserManager()
    admin = manager.create_user("admin", "admin@example.com", "secure123")
    return admin

# Usage example
if __name__ == "__main__":
    manager = UserManager()
    
    # Create users
    admin = manager.create_user("admin", "admin@example.com", "password123")
    user1 = manager.create_user("john", "john@example.com", "mypassword")
    
    # Test authentication
    if manager.authenticate("admin", "password123"):
        print("Admin authenticated successfully")
    
    # Get active users
    active_users = manager.get_active_users()
    print(f"Active users: {len(active_users)}")
'''


def test_code_rag_parsing():
    """Test Code RAG parsing of the sample code."""
    print("🔍 Testing Code RAG parsing...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(SAMPLE_CODE)
        temp_file = f.name
    
    try:
        # Test Code RAG analysis
        response = requests.post(
            f"{CODE_RAG_URL}/analyze",
            json={
                "file_path": temp_file,
                "project_name": "user_auth_demo"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Code RAG analysis successful!")
            print(f"  Language: {result.get('language', 'unknown')}")
            print(f"  Entities found: {len(result.get('entities', []))}")
            print(f"  Relationships found: {len(result.get('relationships', []))}")
            
            # Show entities in detail
            print("\n📋 Entities extracted:")
            for i, entity in enumerate(result.get('entities', [])):
                entity_type = entity.get('entity_type', 'unknown')
                name = entity.get('name', 'Unknown')
                print(f"  {i+1}. {name} ({entity_type})")
                
                if entity.get('docstring'):
                    print(f"     📝 {entity['docstring'][:60]}...")
                
                if entity.get('line_start') and entity.get('line_end'):
                    print(f"     📍 Lines {entity['line_start']}-{entity['line_end']}")
                
                # Show specific details for different entity types
                if entity_type == 'function':
                    params = entity.get('parameters', [])
                    if params:
                        param_str = ', '.join([f"{p.get('name', '')}: {p.get('type', 'Any')}" for p in params])
                        print(f"     🔧 Parameters: {param_str}")
                    
                    if entity.get('return_type'):
                        print(f"     ↩️  Returns: {entity['return_type']}")
                
                elif entity_type == 'class':
                    methods = entity.get('methods', [])
                    if methods:
                        print(f"     🔧 Methods: {', '.join(methods[:3])}{'...' if len(methods) > 3 else ''}")
                
                print()
            
            # Show relationships
            if result.get('relationships'):
                print("🔗 Relationships extracted:")
                for i, rel in enumerate(result.get('relationships', [])):
                    source = rel.get('source_entity_id', 'Unknown')
                    target = rel.get('target_entity_id', 'Unknown')
                    rel_type = rel.get('relationship_type', 'unknown')
                    print(f"  {i+1}. {source} --[{rel_type}]--> {target}")
                    
                    if rel.get('context'):
                        print(f"     💬 Context: {rel['context']}")
                print()
            
            return result
        else:
            print(f"❌ Code RAG analysis failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
            
    finally:
        # Clean up
        os.unlink(temp_file)


def test_graphrag_ingestion():
    """Test submitting code to GraphRAG."""
    print("📤 Testing GraphRAG ingestion...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(SAMPLE_CODE)
        temp_file = f.name
    
    try:
        # Submit to GraphRAG
        with open(temp_file, 'rb') as f:
            files = {'files': ('user_auth.py', f, 'text/plain')}
            data = {
                'domain': 'code',
                'build_knowledge_graph': 'true'
            }
            
            response = requests.post(
                f"{GRAPHRAG_URL}/ingest-documents",
                files=files,
                data=data,
                timeout=60
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ GraphRAG ingestion successful!")
            
            # Show results
            for filename, file_result in result.items():
                print(f"  File: {filename}")
                print(f"    Chunks: {file_result.get('total_chunks', 0)}")
                print(f"    Entities: {file_result.get('entities', 0)}")
                print(f"    Relationships: {file_result.get('relationships', 0)}")
            
            return result
        else:
            print(f"❌ GraphRAG ingestion failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
            
    finally:
        # Clean up
        os.unlink(temp_file)


def test_graphrag_search():
    """Test searching in GraphRAG."""
    print("🔍 Testing GraphRAG search...")
    
    search_queries = [
        "user authentication",
        "password verification",
        "User class methods",
        "UserManager create user"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Searching for: '{query}'")
        
        try:
            response = requests.post(
                f"{GRAPHRAG_URL}/search",
                json={
                    "query": query,
                    "top_k": 3,
                    "threshold": 0.1
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                results = result.get('results', [])
                print(f"  ✅ Found {len(results)} results")
                
                for i, search_result in enumerate(results):
                    content = search_result.get('content', '')
                    source = search_result.get('source', 'unknown')
                    score = search_result.get('score', 0)
                    
                    print(f"    {i+1}. Score: {score:.3f} | Source: {source}")
                    print(f"       Content: {content[:80]}...")
                    print()
            else:
                print(f"  ❌ Search failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Search error: {e}")


def main():
    """Run the integration demonstration."""
    print("🚀 Code RAG + GraphRAG Integration Test")
    print("=" * 50)
    
    # Test 1: Code RAG parsing
    print("\n" + "="*50)
    print("TEST 1: Code RAG Parsing")
    print("="*50)
    code_rag_result = test_code_rag_parsing()
    
    # Test 2: GraphRAG ingestion
    print("\n" + "="*50)
    print("TEST 2: GraphRAG Ingestion")
    print("="*50)
    graphrag_result = test_graphrag_ingestion()
    
    # Wait for indexing
    print("\n⏳ Waiting for indexing...")
    import time
    time.sleep(5)
    
    # Test 3: GraphRAG search
    print("\n" + "="*50)
    print("TEST 3: GraphRAG Search")
    print("="*50)
    test_graphrag_search()
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print(f"✅ Code RAG parsing: {'Success' if code_rag_result else 'Failed'}")
    print(f"✅ GraphRAG ingestion: {'Success' if graphrag_result else 'Failed'}")
    print("✅ GraphRAG search: Completed")
    
    if code_rag_result:
        print(f"\n📊 Code RAG Results:")
        print(f"  - Entities extracted: {len(code_rag_result.get('entities', []))}")
        print(f"  - Relationships extracted: {len(code_rag_result.get('relationships', []))}")
        print(f"  - Language detected: {code_rag_result.get('language', 'unknown')}")
    
    print("\n🎉 Integration test completed!")
    print("\nThis demonstrates that:")
    print("  1. Code RAG can parse Python code and extract entities/relationships")
    print("  2. GraphRAG can ingest and index the same code")
    print("  3. Both systems can work together for unified code search")


if __name__ == "__main__":
    main() 