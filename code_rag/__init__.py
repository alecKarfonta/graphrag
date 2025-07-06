"""
Code RAG - Intelligent Code Search and Retrieval System
"""

__version__ = "1.0.0"
__author__ = "Code RAG Team"
__description__ = "Semantic code search using embeddings and knowledge graphs"

# Core models (always available)
from .models.entities import (
    FunctionEntity, ClassEntity, VariableEntity, ModuleEntity,
    RelationshipEntity, ParseResult, EntityType, RelationshipType
)

# Optional imports (require dependencies)
try:
    from .parsers.python_parser import PythonParser
    _PARSERS_AVAILABLE = True
except ImportError:
    _PARSERS_AVAILABLE = False
    PythonParser = None

try:
    from .search.search_engine import CodeSearchEngine, SearchContext
    _SEARCH_AVAILABLE = True
except ImportError:
    _SEARCH_AVAILABLE = False
    CodeSearchEngine = None
    SearchContext = None

try:
    from .vectorstore.embeddings import CodeEmbedder
    _EMBEDDINGS_AVAILABLE = True
except ImportError:
    _EMBEDDINGS_AVAILABLE = False
    CodeEmbedder = None

__all__ = [
    "FunctionEntity",
    "ClassEntity", 
    "VariableEntity",
    "ModuleEntity",
    "RelationshipEntity",
    "ParseResult",
    "EntityType",
    "RelationshipType",
    "PythonParser",
    "CodeSearchEngine", 
    "SearchContext",
    "CodeEmbedder"
]

# Availability flags
__features__ = {
    "parsers": _PARSERS_AVAILABLE,
    "search": _SEARCH_AVAILABLE,
    "embeddings": _EMBEDDINGS_AVAILABLE
} 