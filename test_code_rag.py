"""
Tests for Code RAG system.
"""

import pytest
import tempfile
import os
from pathlib import Path

from code_rag.parsers.python_parser import PythonParser
from code_rag.search.search_engine import CodeSearchEngine, SearchContext
from code_rag.vectorstore.embeddings import CodeEmbedder
from code_rag.models.entities import EntityType, FunctionEntity, ClassEntity


# Sample Python code for testing
SAMPLE_PYTHON_CODE = '''
"""Sample module for testing."""

import os
import json
from typing import List, Dict, Optional

class UserManager:
    """Manages user operations and authentication."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connected = False
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user with username and password."""
        if not username or not password:
            return False
        
        hashed_password = self._hash_password(password)
        user = self._get_user_from_database(username)
        
        if user and user.get("password_hash") == hashed_password:
            self._create_session(user["id"])
            return True
        
        return False
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _get_user_from_database(self, username: str) -> Optional[Dict]:
        """Retrieve user from database."""
        # Simulate database lookup
        return {"id": 1, "username": username, "password_hash": "dummy_hash"}
    
    def _create_session(self, user_id: int):
        """Create a user session."""
        pass

def log_message(level: str, message: str):
    """Log a message with specified level."""
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{timestamp}] {level.upper()}: {message}")

def parse_json_file(file_path: str) -> Dict:
    """Parse a JSON file and return the data."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log_message("error", f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        log_message("error", f"Invalid JSON in {file_path}: {e}")
        return {}

# Global constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
'''


class TestPythonParser:
    """Test the Python parser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PythonParser()
        
        # Create temporary file with sample code
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write(SAMPLE_PYTHON_CODE)
        self.temp_file.close()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)
    
    def test_can_parse_python_files(self):
        """Test that parser can identify Python files."""
        assert self.parser.can_parse("test.py")
        assert self.parser.can_parse("test.pyw")
        assert not self.parser.can_parse("test.js")
        assert not self.parser.can_parse("test.txt")
    
    def test_parse_file_success(self):
        """Test successful file parsing."""
        result = self.parser.parse_file(self.temp_file.name)
        
        assert result.success
        assert result.language == "python"
        assert result.file_path == self.temp_file.name
        assert len(result.entities) > 0
        assert result.parse_time_ms > 0
    
    def test_extract_functions(self):
        """Test function extraction."""
        result = self.parser.parse_file(self.temp_file.name)
        
        # Find functions
        functions = [e for e in result.entities if isinstance(e, FunctionEntity)]
        function_names = [f.name for f in functions]
        
        assert "authenticate_user" in function_names
        assert "log_message" in function_names
        assert "parse_json_file" in function_names
        assert "_hash_password" in function_names
        
        # Check function details
        auth_func = next(f for f in functions if f.name == "authenticate_user")
        assert auth_func.is_method
        assert len(auth_func.parameters) == 3  # self, username, password
        assert auth_func.return_type == "bool"
        assert auth_func.docstring is not None
        assert auth_func.complexity > 1  # Has if statements
    
    def test_extract_classes(self):
        """Test class extraction."""
        result = self.parser.parse_file(self.temp_file.name)
        
        # Find classes
        classes = [e for e in result.entities if isinstance(e, ClassEntity)]
        class_names = [c.name for c in classes]
        
        assert "UserManager" in class_names
        
        # Check class details
        user_manager = next(c for c in classes if c.name == "UserManager")
        assert user_manager.docstring is not None
        assert len(user_manager.methods) > 0
        assert "authenticate_user" in user_manager.methods
    
    def test_extract_variables(self):
        """Test variable extraction."""
        result = self.parser.parse_file(self.temp_file.name)
        
        # Find variables
        variables = [e for e in result.entities if e.entity_type == EntityType.VARIABLE]
        variable_names = [v.name for v in variables]
        
        assert "MAX_RETRIES" in variable_names
        assert "DEFAULT_TIMEOUT" in variable_names
        
        # Check variable details
        max_retries = next(v for v in variables if v.name == "MAX_RETRIES")
        assert max_retries.is_constant
        assert max_retries.initial_value == "3"
    
    def test_extract_imports(self):
        """Test import extraction."""
        result = self.parser.parse_file(self.temp_file.name)
        
        # Find module entity
        modules = [e for e in result.entities if e.entity_type == EntityType.MODULE]
        assert len(modules) == 1
        
        module = modules[0]
        imports = module.imports
        
        assert "os" in imports
        assert "json" in imports
        assert "typing.List" in imports
        assert "typing.Dict" in imports
        assert "typing.Optional" in imports


class TestCodeEmbedder:
    """Test the code embedder."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use a smaller model for testing
        self.embedder = CodeEmbedder("microsoft/codebert-base")
        
        # Create sample entities
        self.sample_function = FunctionEntity(
            name="authenticate_user",
            entity_type=EntityType.FUNCTION,
            file_path="test.py",
            line_start=10,
            line_end=20,
            language="python",
            parameters=[
                {"name": "username", "type": "str"},
                {"name": "password", "type": "str"}
            ],
            return_type="bool",
            docstring="Authenticate a user with username and password."
        )
        
        self.sample_class = ClassEntity(
            name="UserManager",
            entity_type=EntityType.CLASS,
            file_path="test.py",
            line_start=5,
            line_end=25,
            language="python",
            methods=["authenticate_user", "create_user"],
            docstring="Manages user operations."
        )
    
    def test_embed_function(self):
        """Test function embedding generation."""
        embedding = self.embedder.embed_function(self.sample_function)
        
        assert embedding is not None
        assert len(embedding) > 0
        assert isinstance(embedding[0], float)
    
    def test_embed_class(self):
        """Test class embedding generation."""
        embedding = self.embedder.embed_class(self.sample_class)
        
        assert embedding is not None
        assert len(embedding) > 0
        assert isinstance(embedding[0], float)
    
    def test_embed_query(self):
        """Test query embedding generation."""
        embedding = self.embedder.embed_query("user authentication")
        
        assert embedding is not None
        assert len(embedding) > 0
        assert isinstance(embedding[0], float)
    
    def test_similarity_calculation(self):
        """Test similarity calculation between embeddings."""
        func_embedding = self.embedder.embed_function(self.sample_function)
        query_embedding = self.embedder.embed_query("authenticate user")
        
        similarity = self.embedder.calculate_similarity(func_embedding, query_embedding)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.1  # Should have some similarity
    
    def test_embedding_cache(self):
        """Test embedding caching."""
        # First call
        embedding1 = self.embedder.embed_function(self.sample_function)
        cache_size1 = self.embedder.get_cache_size()
        
        # Second call (should use cache)
        embedding2 = self.embedder.embed_function(self.sample_function)
        cache_size2 = self.embedder.get_cache_size()
        
        assert cache_size1 == cache_size2  # Cache size shouldn't increase
        assert (embedding1 == embedding2).all()  # Should be identical


class TestCodeSearchEngine:
    """Test the code search engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.search_engine = CodeSearchEngine()
        
        # Create sample entities
        self.entities = [
            FunctionEntity(
                name="authenticate_user",
                entity_type=EntityType.FUNCTION,
                file_path="auth.py",
                line_start=10,
                line_end=20,
                language="python",
                docstring="Authenticate a user with username and password.",
                calls=["hash_password", "get_user_from_database"]
            ),
            FunctionEntity(
                name="hash_password",
                entity_type=EntityType.FUNCTION,
                file_path="auth.py",
                line_start=25,
                line_end=30,
                language="python",
                docstring="Hash a password using SHA-256."
            ),
            ClassEntity(
                name="UserManager",
                entity_type=EntityType.CLASS,
                file_path="user.py",
                line_start=5,
                line_end=50,
                language="python",
                methods=["create_user", "delete_user", "authenticate_user"],
                docstring="Manages user operations and authentication."
            ),
            FunctionEntity(
                name="log_message",
                entity_type=EntityType.FUNCTION,
                file_path="logger.py",
                line_start=5,
                line_end=10,
                language="python",
                docstring="Log a message with specified level."
            )
        ]
        
        # Add entities to search engine
        self.search_engine.add_entities(self.entities)
    
    def test_semantic_search(self):
        """Test semantic search functionality."""
        response = self.search_engine.search("user authentication", top_k=5)
        
        assert response.total_results > 0
        assert response.search_time_ms > 0
        assert len(response.results) <= 5
        
        # Should find authentication-related entities
        result_names = [r.entity.name for r in response.results]
        assert "authenticate_user" in result_names
    
    def test_exact_search(self):
        """Test exact name matching."""
        response = self.search_engine.search("UserManager", top_k=5)
        
        assert response.total_results > 0
        
        # Should find exact match first
        top_result = response.results[0]
        assert top_result.entity.name == "UserManager"
        assert top_result.score == 1.0
    
    def test_structural_search(self):
        """Test structural search (relationships)."""
        response = self.search_engine.search("calls hash_password", top_k=5)
        
        # Should find functions that call hash_password
        result_names = [r.entity.name for r in response.results]
        assert "authenticate_user" in result_names
    
    def test_functional_search(self):
        """Test functional search (by purpose)."""
        response = self.search_engine.search("logging", top_k=5)
        
        assert response.total_results > 0
        
        # Should find logging-related entities
        result_names = [r.entity.name for r in response.results]
        assert "log_message" in result_names
    
    def test_context_filtering(self):
        """Test search with context filtering."""
        context = SearchContext(language="python")
        response = self.search_engine.search("authentication", context=context, top_k=5)
        
        # All results should be Python
        for result in response.results:
            assert result.entity.language == "python"
    
    def test_suggestions_generation(self):
        """Test search suggestions."""
        response = self.search_engine.search("nonexistent_function", top_k=5)
        
        # Should generate suggestions when no results found
        if response.total_results == 0:
            assert len(response.suggestions) > 0
    
    def test_search_statistics(self):
        """Test search engine statistics."""
        stats = self.search_engine.get_statistics()
        
        assert stats["total_entities"] == len(self.entities)
        assert stats["indexed"] is True
        assert "entity_counts" in stats
        
        # Check entity type counts
        entity_counts = stats["entity_counts"]
        assert entity_counts["function"] == 3  # authenticate_user, hash_password, log_message
        assert entity_counts["class"] == 1     # UserManager


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from parsing to searching."""
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_file.write(SAMPLE_PYTHON_CODE)
        temp_file.close()
        
        try:
            # 1. Parse the file
            parser = PythonParser()
            parse_result = parser.parse_file(temp_file.name)
            
            assert parse_result.success
            assert len(parse_result.entities) > 0
            
            # 2. Index the entities
            search_engine = CodeSearchEngine()
            search_engine.add_entities(parse_result.entities)
            
            # 3. Search for entities
            test_queries = [
                "authentication",
                "UserManager",
                "JSON parsing",
                "logging",
                "password hashing"
            ]
            
            for query in test_queries:
                response = search_engine.search(query, top_k=3)
                
                # Should get some results for most queries
                assert response.search_time_ms > 0
                # Some queries might not have results, which is OK
                
                if response.total_results > 0:
                    # Check result quality
                    for result in response.results:
                        assert 0.0 <= result.score <= 1.0
                        assert result.entity is not None
                        assert result.explanation is not None
        
        finally:
            os.unlink(temp_file.name)
    
    def test_multiple_file_indexing(self):
        """Test indexing multiple files."""
        # Create multiple temporary files
        files = []
        codes = [
            '''
def function_a():
    """Function in file A."""
    pass
            ''',
            '''
class ClassB:
    """Class in file B."""
    def method_b(self):
        pass
            ''',
            '''
def function_c():
    """Function in file C."""
    function_a()  # Call function from file A
            '''
        ]
        
        try:
            for i, code in enumerate(codes):
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'_{i}.py', delete=False)
                temp_file.write(code)
                temp_file.close()
                files.append(temp_file.name)
            
            # Parse all files
            parser = PythonParser()
            all_entities = []
            
            for file_path in files:
                result = parser.parse_file(file_path)
                if result.success:
                    all_entities.extend(result.entities)
            
            # Index all entities
            search_engine = CodeSearchEngine()
            search_engine.add_entities(all_entities)
            
            # Search across all files
            response = search_engine.search("function", top_k=10)
            
            assert response.total_results > 0
            
            # Should find entities from different files
            file_paths = set(result.entity.file_path for result in response.results)
            assert len(file_paths) > 1  # Entities from multiple files
        
        finally:
            for file_path in files:
                os.unlink(file_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 