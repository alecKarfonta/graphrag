# Code RAG + GraphRAG Integration Guide

## Overview

This document describes how Code RAG integrates with the main GraphRAG system to provide unified code search and analysis capabilities.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Code Files    │    │   Text Files    │    │   Upload API    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Code Detector                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Python    │  │ JavaScript  │  │    Java     │          │
│  │   Parser    │  │   Parser    │  │   Parser    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────┐              ┌─────────────────┐
│   Code RAG      │              │   GraphRAG      │
│   Processing    │              │   Processing    │
│                 │              │                 │
│ • AST Parsing   │              │ • Text Analysis │
│ • Entity Ext.   │              │ • NER/RE        │
│ • Relationships  │              │ • KG Building   │
│ • Embeddings    │              │ • Vector Store  │
└─────────┬───────┘              └─────────┬───────┘
          │                              │
          └──────────────┬───────────────┘
                         ▼
              ┌─────────────────┐
              │  Unified Search │
              │                 │
              │ • Vector Search │
              │ • Graph Search  │
              │ • Hybrid Search │
              └─────────────────┘
```

## 🔄 Integration Flow

### 1. **File Upload & Detection**

When a file is uploaded to GraphRAG:

```python
# GraphRAG receives file upload
POST /hybrid/process
{
    "file": "code.py",
    "domain": "code"
}

# Code Detector analyzes file
file_info = code_detector.get_code_file_info("code.py")
# Returns: {"is_code": True, "language": "python", ...}
```

### 2. **Routing Decision**

Based on file type, the system routes to appropriate processor:

```python
if file_info["is_code"]:
    # Route to Code RAG for specialized processing
    code_rag_result = code_rag_router.route_file_to_code_rag(file_path)
    # Also send to GraphRAG for unified search
    graphrag_result = send_to_graphrag(file_path)
else:
    # Send only to GraphRAG
    graphrag_result = send_to_graphrag(file_path)
```

### 3. **Code RAG Processing**

Code RAG processes the file and extracts:

```python
# Code RAG Analysis Result
{
    "success": True,
    "language": "python",
    "entities": [
        {
            "name": "UserManager",
            "entity_type": "class",
            "file_path": "code.py",
            "line_start": 5,
            "line_end": 25,
            "methods": ["authenticate_user", "_hash_password"],
            "base_classes": [],
            "docstring": "Manages user operations..."
        },
        {
            "name": "authenticate_user",
            "entity_type": "function",
            "parameters": [{"name": "username", "type": "str"}, ...],
            "return_type": "bool",
            "complexity": 3,
            "calls": ["_hash_password"]
        }
    ],
    "relationships": [
        {
            "source": "authenticate_user",
            "target": "_hash_password",
            "relationship_type": "calls",
            "context": "authenticate_user calls _hash_password"
        }
    ]
}
```

### 4. **GraphRAG Integration**

Code RAG entities are converted to GraphRAG format:

```python
# Convert Code RAG entities to GraphRAG format
graphrag_entities = []
for entity in code_rag_entities:
    graphrag_entity = {
        "name": entity.name,
        "type": entity.entity_type.value.upper(),
        "description": create_entity_description(entity),
        "source_file": entity.file_path,
        "metadata": {
            "language": entity.language,
            "line_start": entity.line_start,
            "line_end": entity.line_end,
            "visibility": entity.visibility.value,
            "code_rag_id": entity.id
        }
    }
    graphrag_entities.append(graphrag_entity)
```

## 🔧 Artifact Compatibility

### **Entity Format Compatibility**

| Code RAG Entity | GraphRAG Entity | Mapping |
|-----------------|-----------------|---------|
| `FunctionEntity` | `Entity` | `name`, `type: "FUNCTION"`, `description` |
| `ClassEntity` | `Entity` | `name`, `type: "CLASS"`, `description` |
| `VariableEntity` | `Entity` | `name`, `type: "VARIABLE"`, `description` |
| `ModuleEntity` | `Entity` | `name`, `type: "MODULE"`, `description` |

### **Relationship Format Compatibility**

| Code RAG Relationship | GraphRAG Relationship | Mapping |
|----------------------|----------------------|---------|
| `CALLS` | `RELATES_TO` | `source`, `target`, `relation: "CALLS"` |
| `INHERITS` | `RELATES_TO` | `source`, `target`, `relation: "INHERITS"` |
| `USES` | `RELATES_TO` | `source`, `target`, `relation: "USES"` |
| `CONTAINS` | `RELATES_TO` | `source`, `target`, `relation: "CONTAINS"` |

### **Vector Embedding Compatibility**

Both systems use compatible vector formats:

```python
# Code RAG Embedding
code_embedding = code_embedder.embed_entity(function_entity)
# Shape: (768,) - CodeBERT embedding

# GraphRAG Embedding  
graphrag_embedding = graphrag_embedder.embed_text(entity_description)
# Shape: (384,) - SentenceTransformer embedding

# Both can be stored in Qdrant vector database
```

## 🚀 API Endpoints

### **Code Detection Endpoints**

```bash
# Detect if file is code
POST /code-detection/detect
{
    "file": "uploaded_file.py"
}

# Route code file to Code RAG
POST /code-detection/route
{
    "file": "uploaded_file.py",
    "project_name": "my_project"
}
```

### **Hybrid Processing Endpoints**

```bash
# Process file with hybrid approach
POST /hybrid/process
{
    "file": "uploaded_file.py",
    "domain": "code"
}

# Get system status
GET /hybrid/status

# Search for code in GraphRAG
POST /search/code
{
    "query": "user authentication function",
    "top_k": 10
}
```

## 📊 Data Flow Examples

### **Example 1: Python File Processing**

```python
# Input: user_manager.py
class UserManager:
    def authenticate_user(self, username: str, password: str) -> bool:
        # Implementation...

# Code RAG Processing:
entities = [
    {"name": "UserManager", "type": "class", "methods": ["authenticate_user"]},
    {"name": "authenticate_user", "type": "function", "parameters": [...]}
]

relationships = [
    {"source": "authenticate_user", "target": "_hash_password", "type": "calls"}
]

# GraphRAG Integration:
graphrag_entities = [
    {
        "name": "UserManager",
        "type": "CLASS", 
        "description": "Class UserManager - Manages user operations",
        "metadata": {"language": "python", "line_start": 1, ...}
    }
]
```

### **Example 2: Search Query Processing**

```python
# Query: "find authentication functions"
# GraphRAG searches both:
# 1. Vector similarity in Qdrant
# 2. Graph relationships in Neo4j

# Results from both systems:
results = [
    {
        "content": "def authenticate_user(username: str, password: str) -> bool:",
        "source": "user_manager.py",
        "score": 0.95,
        "result_type": "vector"
    },
    {
        "content": "UserManager.authenticate_user calls _hash_password",
        "source": "graph",
        "score": 0.88,
        "result_type": "graph"
    }
]
```

## 🔍 Search Capabilities

### **Unified Search Features**

1. **Semantic Code Search**: "authentication logic" → finds relevant functions
2. **Structural Search**: "classes that inherit from BaseModel" → finds inheritance relationships
3. **Pattern Search**: "singleton implementations" → finds design patterns
4. **Cross-Language Search**: "database connection" → finds code across languages

### **Search Examples**

```bash
# Find authentication functions
curl -X POST "http://localhost:8000/search/code" \
  -H "Content-Type: application/json" \
  -d '{"query": "user authentication", "top_k": 5}'

# Find classes with specific methods
curl -X POST "http://localhost:8000/search/code" \
  -H "Content-Type: application/json" \
  -d '{"query": "classes with save method", "top_k": 5}'

# Find code that uses specific libraries
curl -X POST "http://localhost:8000/search/code" \
  -H "Content-Type: application/json" \
  -d '{"query": "code using pandas", "top_k": 5}'
```

## 🧪 Testing Integration

### **Test Scenarios**

1. **Code Detection**: Verify Python/JS/Java files are correctly identified
2. **Hybrid Processing**: Ensure code files go to both systems
3. **Entity Conversion**: Validate Code RAG → GraphRAG entity mapping
4. **Unified Search**: Test that code entities appear in GraphRAG search
5. **Performance**: Measure processing time for large codebases

### **Test Commands**

```bash
# Test code detection
python test_code_rag_integration.py -k "test_code_detection"

# Test hybrid processing
python test_code_rag_integration.py -k "test_hybrid_processing"

# Test end-to-end workflow
python test_code_rag_integration.py -k "test_complete_workflow"
```

## 📈 Performance Considerations

### **Processing Times**

| Operation | Code RAG | GraphRAG | Combined |
|-----------|----------|----------|----------|
| Python file (1000 LOC) | ~50ms | ~100ms | ~150ms |
| JavaScript file (500 LOC) | ~30ms | ~80ms | ~110ms |
| Java file (2000 LOC) | ~80ms | ~120ms | ~200ms |

### **Storage Requirements**

| Component | Size per 1000 entities |
|-----------|------------------------|
| Code RAG vectors | ~3MB |
| GraphRAG vectors | ~1.5MB |
| Knowledge graph | ~2MB |
| **Total** | **~6.5MB** |

## 🔧 Configuration

### **Environment Variables**

```bash
# GraphRAG Configuration
GRAPH_RAG_API_URL=http://localhost:8000
QDRANT_URL=http://localhost:6333
NEO4J_URI=bolt://localhost:7687

# Code RAG Configuration  
CODE_RAG_API_URL=http://localhost:8003
CODE_RAG_MODEL=microsoft/codebert-base

# Integration Configuration
ENABLE_CODE_DETECTION=true
ENABLE_HYBRID_PROCESSING=true
CODE_DOMAIN=code
```

### **Docker Compose Setup**

```yaml
services:
  graphrag-api:
    # ... existing config
    environment:
      - ENABLE_CODE_DETECTION=true
      - CODE_RAG_API_URL=http://code-rag-api:8003
  
  code-rag-api:
    build: ./code_rag
    ports:
      - "8003:8000"
    environment:
      - GRAPH_RAG_API_URL=http://graphrag-api:8000
```

## 🚀 Deployment

### **Quick Start**

```bash
# 1. Start GraphRAG
docker-compose up -d

# 2. Start Code RAG
cd code_rag
docker-compose up -d

# 3. Test integration
curl http://localhost:8000/hybrid/status

# 4. Upload and process code
curl -X POST http://localhost:8000/hybrid/process \
  -F "file=@my_code.py" \
  -F "domain=code"

# 5. Search for code
curl -X POST http://localhost:8000/search/code \
  -H "Content-Type: application/json" \
  -d '{"query": "authentication", "top_k": 5}'
```

## ✅ Verification Checklist

- [ ] Code detection correctly identifies Python/JS/Java files
- [ ] Code RAG processes files and extracts entities
- [ ] Entities are converted to GraphRAG format
- [ ] Relationships are mapped correctly
- [ ] Vectors are stored in unified vector database
- [ ] GraphRAG search returns code-related results
- [ ] Hybrid processing works for both code and text files
- [ ] Performance is acceptable for large codebases
- [ ] Error handling works for malformed code files

## 🎯 Benefits

1. **Unified Search**: Find code and documentation in one place
2. **Semantic Understanding**: Code-aware search beyond text matching
3. **Cross-Reference**: Link code to documentation and vice versa
4. **Scalable**: Handle large codebases efficiently
5. **Extensible**: Easy to add new language parsers

The integration provides a powerful unified system for code search and analysis! 🚀 