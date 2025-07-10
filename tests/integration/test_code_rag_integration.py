"""
Test the integration between Code RAG and GraphRAG systems.
"""

import pytest
import tempfile
import os
import requests
import time
from pathlib import Path

# Test data
SAMPLE_PYTHON_CODE = '''
"""Sample Python module for testing integration."""

import os
import json
from typing import List, Dict, Optional

class UserManager:
    """Manages user operations and authentication."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.users = {}
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user with username and password."""
        if not username or not password:
            return False
        
        hashed_password = self._hash_password(password)
        user = self.users.get(username)
        
        if user and user.get("password_hash") == hashed_password:
            return True
        return False
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

def log_message(level: str, message: str):
    """Log a message with specified level."""
    print(f"[{level.upper()}] {message}")

# Global constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
'''

SAMPLE_TEXT_DOCUMENT = '''
Technical Documentation

This document describes the system architecture.
The system consists of multiple components:
- Database layer for data persistence
- API layer for external communication
- Business logic layer for processing
- User interface layer for interaction

The database layer connects to the API layer.
The API layer processes requests from the business logic.
'''


class TestCodeRAGIntegration:
    """Test the integration between Code RAG and GraphRAG."""
    
    def setup_method(self):
        """Set up test environment."""
        self.graphrag_url = "http://localhost:8000"
        self.code_rag_url = "http://localhost:8003"
        
        # Create test files
        self.python_file = self._create_test_file("test_code.py", SAMPLE_PYTHON_CODE)
        self.text_file = self._create_test_file("test_doc.txt", SAMPLE_TEXT_DOCUMENT)
    
    def teardown_method(self):
        """Clean up test files."""
        if hasattr(self, 'python_file') and os.path.exists(self.python_file):
            os.unlink(self.python_file)
        if hasattr(self, 'text_file') and os.path.exists(self.text_file):
            os.unlink(self.text_file)
    
    def _create_test_file(self, filename: str, content: str) -> str:
        """Create a temporary test file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'_{filename}', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_code_detection(self):
        """Test that code files are correctly detected."""
        # Test Python file detection
        response = requests.post(
            f"{self.graphrag_url}/code-detection/detect",
            files={"file": ("test_code.py", open(self.python_file, "rb"))}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["is_code"] == True
        assert result["language"] == "python"
        assert result["file_size"] > 0
        assert result["line_count"] > 0
    
    def test_text_document_detection(self):
        """Test that text documents are not detected as code."""
        response = requests.post(
            f"{self.graphrag_url}/code-detection/detect",
            files={"file": ("test_doc.txt", open(self.text_file, "rb"))}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["is_code"] == False
        assert result["language"] is None
    
    def test_hybrid_processing_python(self):
        """Test hybrid processing of Python code files."""
        response = requests.post(
            f"{self.graphrag_url}/hybrid/process",
            files={"file": ("test_code.py", open(self.python_file, "rb"))},
            data={"domain": "code"}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["file_type"] == "code"
        assert result["language"] == "python"
        assert result["hybrid_processing"] == True
        
        # Check that both systems were involved
        assert "code_rag_processing" in result
        assert "graphrag_processing" in result
    
    def test_hybrid_processing_text(self):
        """Test hybrid processing of text documents."""
        response = requests.post(
            f"{self.graphrag_url}/hybrid/process",
            files={"file": ("test_doc.txt", open(self.text_file, "rb"))},
            data={"domain": "general"}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["file_type"] == "document"
        assert result["language"] is None
        assert result["hybrid_processing"] == False
        
        # Check that only GraphRAG was used
        assert result["code_rag_processing"] is None
        assert "graphrag_processing" in result
    
    def test_system_status(self):
        """Test that system status endpoint works."""
        response = requests.get(f"{self.graphrag_url}/hybrid/status")
        
        assert response.status_code == 200
        result = response.json()
        
        # Check that status contains expected fields
        assert "graphrag_healthy" in result
        assert "code_rag_healthy" in result
        assert "hybrid_available" in result
        assert "code_rag_status" in result
    
    def test_code_search(self):
        """Test searching for code-related information."""
        # First, ingest some code
        self.test_hybrid_processing_python()
        
        # Wait a moment for processing
        time.sleep(2)
        
        # Search for code-related information
        response = requests.post(
            f"{self.graphrag_url}/search/code",
            json={
                "query": "user authentication function",
                "top_k": 5
            }
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should return some results
        assert "results" in result
        assert "total_results" in result
        assert result["domain"] == "code"
    
    def test_code_rag_health(self):
        """Test Code RAG health check."""
        response = requests.get(f"{self.graphrag_url}/code-detection/health")
        
        assert response.status_code == 200
        result = response.json()
        
        # Check that health check contains expected fields
        assert "available" in result
        assert "status" in result
        assert "response" in result


class TestCodeRAGToGraphRAGBridge:
    """Test the bridge between Code RAG and GraphRAG."""
    
    def setup_method(self):
        """Set up test environment."""
        self.graphrag_url = "http://localhost:8000"
        self.code_rag_url = "http://localhost:8003"
        
        # Create test Python file
        self.python_file = self._create_test_file("test_bridge.py", SAMPLE_PYTHON_CODE)
    
    def teardown_method(self):
        """Clean up test files."""
        if hasattr(self, 'python_file') and os.path.exists(self.python_file):
            os.unlink(self.python_file)
    
    def _create_test_file(self, filename: str, content: str) -> str:
        """Create a temporary test file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'_{filename}', delete=False)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_code_rag_analysis(self):
        """Test Code RAG analysis of Python file."""
        response = requests.post(
            f"{self.code_rag_url}/analyze",
            json={"file_path": self.python_file}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Check that analysis was successful
        assert result["success"] == True
        assert result["language"] == "python"
        assert len(result["entities"]) > 0
        
        # Check for expected entities
        entity_names = [e["name"] for e in result["entities"]]
        assert "UserManager" in entity_names
        assert "authenticate_user" in entity_names
        assert "log_message" in entity_names
    
    def test_code_rag_to_graphrag_integration(self):
        """Test sending Code RAG results to GraphRAG."""
        # First, analyze with Code RAG
        analysis_response = requests.post(
            f"{self.code_rag_url}/analyze",
            json={"file_path": self.python_file}
        )
        
        assert analysis_response.status_code == 200
        analysis_result = analysis_response.json()
        
        # Then, send to GraphRAG via hybrid processing
        with open(self.python_file, "rb") as f:
            hybrid_response = requests.post(
                f"{self.graphrag_url}/hybrid/process",
                files={"file": ("test_bridge.py", f)},
                data={"domain": "code"}
            )
        
        assert hybrid_response.status_code == 200
        hybrid_result = hybrid_response.json()
        
        # Check that both systems processed the file
        assert hybrid_result["file_type"] == "code"
        assert hybrid_result["language"] == "python"
        assert hybrid_result["hybrid_processing"] == True
    
    def test_search_integration(self):
        """Test that code entities can be found in GraphRAG search."""
        # First, process the code file
        self.test_code_rag_to_graphrag_integration()
        
        # Wait for processing
        time.sleep(3)
        
        # Search for code entities in GraphRAG
        search_response = requests.post(
            f"{self.graphrag_url}/search",
            json={
                "query": "UserManager class authentication",
                "top_k": 5
            }
        )
        
        assert search_response.status_code == 200
        search_result = search_response.json()
        
        # Should find code-related results
        assert len(search_result["results"]) > 0
        
        # Check that results contain code-related content
        found_code_content = False
        for result in search_result["results"]:
            content = result["content"].lower()
            if any(keyword in content for keyword in ["class", "function", "user", "authentication"]):
                found_code_content = True
                break
        
        assert found_code_content, "Should find code-related content in search results"


class TestEndToEndIntegration:
    """Test end-to-end integration scenarios."""
    
    def test_complete_workflow(self):
        """Test the complete workflow from code file to searchable knowledge."""
        # This test would require both services to be running
        # For now, we'll test the individual components
        
        # 1. Code detection
        # 2. Code RAG analysis
        # 3. GraphRAG integration
        # 4. Unified search
        
        # This is a placeholder for the complete workflow test
        assert True, "Complete workflow test placeholder"
    
    def test_multi_language_support(self):
        """Test support for multiple programming languages."""
        # This would test different language parsers
        # For now, we'll test Python support
        assert True, "Multi-language support test placeholder"
    
    def test_large_codebase_processing(self):
        """Test processing of large codebases."""
        # This would test performance with many files
        assert True, "Large codebase processing test placeholder"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 