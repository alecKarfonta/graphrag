# Code RAG Technical Architecture

## System Overview

The Code RAG system is designed as a microservices architecture that can scale horizontally and handle large codebases efficiently. The system combines traditional information retrieval with advanced code understanding and graph-based reasoning.

## Core Components Architecture

### 1. Code Ingestion Pipeline

```python
# ingestion/pipeline.py
class CodeIngestionPipeline:
    def __init__(self):
        self.parsers = {
            '.py': PythonParser(),
            '.js': JavaScriptParser(),
            '.ts': TypeScriptParser(),
            '.java': JavaParser(),
            '.cpp': CppParser(),
            '.go': GoParser(),
            '.rs': RustParser()
        }
        self.entity_extractor = CodeEntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
        self.embedder = CodeEmbedder()
        self.graph_builder = CodeGraphBuilder()
        
    async def process_repository(self, repo_path: str) -> IngestionResult:
        """Process entire repository and build knowledge graph."""
        files = self.discover_code_files(repo_path)
        
        # Phase 1: Parse all files and extract entities
        entities = []
        for file_path in files:
            file_entities = await self.process_file(file_path)
            entities.extend(file_entities)
        
        # Phase 2: Extract relationships between entities
        relationships = self.relationship_extractor.extract_all(entities)
        
        # Phase 3: Build knowledge graph
        await self.graph_builder.build_graph(entities, relationships)
        
        # Phase 4: Generate and store embeddings
        await self.embedder.embed_entities(entities)
        
        return IngestionResult(
            files_processed=len(files),
            entities_extracted=len(entities),
            relationships_found=len(relationships)
        )
```

### 2. Multi-Language Parser System

```python
# parsers/base_parser.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseCodeParser(ABC):
    @abstractmethod
    def parse_file(self, file_path: str) -> ParseResult:
        pass
    
    @abstractmethod
    def extract_functions(self, ast_tree) -> List[FunctionEntity]:
        pass
    
    @abstractmethod
    def extract_classes(self, ast_tree) -> List[ClassEntity]:
        pass
    
    @abstractmethod
    def extract_imports(self, ast_tree) -> List[ImportEntity]:
        pass

# parsers/python_parser.py
class PythonParser(BaseCodeParser):
    def parse_file(self, file_path: str) -> ParseResult:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code, filename=file_path)
            
            return ParseResult(
                file_path=file_path,
                ast_tree=tree,
                source_code=source_code,
                language='python',
                success=True
            )
        except Exception as e:
            return ParseResult(
                file_path=file_path,
                success=False,
                error=str(e)
            )
    
    def extract_functions(self, ast_tree) -> List[FunctionEntity]:
        functions = []
        for node in ast.walk(ast_tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_entity = FunctionEntity(
                    name=node.name,
                    parameters=self._extract_parameters(node.args),
                    return_type=self._extract_return_type(node),
                    docstring=ast.get_docstring(node),
                    decorators=[self._get_decorator_name(d) for d in node.decorator_list],
                    line_start=node.lineno,
                    line_end=node.end_lineno,
                    complexity=self._calculate_complexity(node),
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                    visibility=self._determine_visibility(node.name)
                )
                functions.append(func_entity)
        return functions
```

### 3. Entity Data Models

```python
# models/entities.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class EntityType(Enum):
    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"
    MODULE = "module"
    INTERFACE = "interface"
    ENUM = "enum"
    STRUCT = "struct"

class Visibility(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    INTERNAL = "internal"

@dataclass
class CodeEntity:
    id: str
    name: str
    entity_type: EntityType
    file_path: str
    line_start: int
    line_end: int
    language: str
    visibility: Visibility
    metadata: Dict[str, Any]

@dataclass
class FunctionEntity(CodeEntity):
    parameters: List[Dict[str, str]]
    return_type: Optional[str]
    docstring: Optional[str]
    decorators: List[str]
    complexity: int
    is_async: bool
    calls: List[str]  # Functions this function calls
    
    def to_search_text(self) -> str:
        """Generate searchable text representation."""
        parts = [
            f"function {self.name}",
            f"parameters: {', '.join([p['name'] for p in self.parameters])}",
            f"returns: {self.return_type or 'None'}",
            self.docstring or "",
            f"decorators: {', '.join(self.decorators)}" if self.decorators else ""
        ]
        return " ".join(filter(None, parts))

@dataclass
class ClassEntity(CodeEntity):
    base_classes: List[str]
    methods: List[str]
    properties: List[str]
    interfaces: List[str]
    design_patterns: List[str]
    is_abstract: bool
    
    def to_search_text(self) -> str:
        parts = [
            f"class {self.name}",
            f"inherits: {', '.join(self.base_classes)}" if self.base_classes else "",
            f"implements: {', '.join(self.interfaces)}" if self.interfaces else "",
            f"methods: {', '.join(self.methods)}",
            f"patterns: {', '.join(self.design_patterns)}" if self.design_patterns else ""
        ]
        return " ".join(filter(None, parts))

@dataclass
class RelationshipEntity:
    id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    context: str
    confidence: float
    metadata: Dict[str, Any]
```

### 4. Knowledge Graph Schema

```cypher
// Neo4j Schema Definition

// Node Types
CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT function_id IF NOT EXISTS FOR (f:Function) REQUIRE f.id IS UNIQUE;
CREATE CONSTRAINT class_id IF NOT EXISTS FOR (c:Class) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT module_id IF NOT EXISTS FOR (m:Module) REQUIRE m.id IS UNIQUE;

// Indexes for Performance
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON e.name;
CREATE INDEX entity_file IF NOT EXISTS FOR (e:Entity) ON e.file_path;
CREATE INDEX entity_language IF NOT EXISTS FOR (e:Entity) ON e.language;
CREATE INDEX function_complexity IF NOT EXISTS FOR (f:Function) ON f.complexity;

// Relationship Types
// CALLS: Function -> Function
// INHERITS: Class -> Class
// IMPLEMENTS: Class -> Interface
// IMPORTS: Module -> Module
// USES: Function -> Variable/Class
// CONTAINS: Module -> Function/Class
// FOLLOWS_PATTERN: Class -> Pattern
```

```python
# graph/schema.py
class GraphSchema:
    """Defines the knowledge graph schema and operations."""
    
    def create_function_node(self, func: FunctionEntity) -> str:
        query = """
        MERGE (f:Function:Entity {id: $id})
        SET f.name = $name,
            f.file_path = $file_path,
            f.line_start = $line_start,
            f.line_end = $line_end,
            f.language = $language,
            f.parameters = $parameters,
            f.return_type = $return_type,
            f.complexity = $complexity,
            f.is_async = $is_async,
            f.visibility = $visibility,
            f.docstring = $docstring,
            f.updated_at = datetime()
        RETURN f.id
        """
        return query
    
    def create_call_relationship(self, caller_id: str, callee_id: str, context: str) -> str:
        query = """
        MATCH (caller:Function {id: $caller_id})
        MATCH (callee:Function {id: $callee_id})
        MERGE (caller)-[r:CALLS]->(callee)
        SET r.context = $context,
            r.created_at = datetime()
        RETURN r
        """
        return query
```

### 5. Vector Embedding System

```python
# embeddings/code_embedder.py
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

class CodeEmbedder:
    def __init__(self, model_name: str = "microsoft/codebert-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        
    def embed_function(self, func: FunctionEntity) -> np.ndarray:
        """Generate embedding for a function."""
        # Combine function signature, docstring, and body
        text_parts = [
            f"def {func.name}({self._format_parameters(func.parameters)}):",
            func.docstring or "",
            # Could include function body here if needed
        ]
        
        text = " ".join(filter(None, text_parts))
        return self._encode_text(text)
    
    def embed_class(self, cls: ClassEntity) -> np.ndarray:
        """Generate embedding for a class."""
        text_parts = [
            f"class {cls.name}",
            f"inherits {', '.join(cls.base_classes)}" if cls.base_classes else "",
            f"methods: {', '.join(cls.methods)}",
            # Include class docstring if available
        ]
        
        text = " ".join(filter(None, text_parts))
        return self._encode_text(text)
    
    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for search query."""
        return self._encode_text(query)
    
    def _encode_text(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use CLS token embedding
            embedding = outputs.last_hidden_state[:, 0, :].numpy()
        
        return embedding.flatten()

# embeddings/specialized_embedders.py
class FunctionEmbedder(CodeEmbedder):
    """Specialized embedder for functions."""
    
    def embed_with_context(self, func: FunctionEntity, context: CodeContext) -> np.ndarray:
        """Embed function with surrounding context."""
        context_text = self._build_context_text(func, context)
        return self._encode_text(context_text)
    
    def _build_context_text(self, func: FunctionEntity, context: CodeContext) -> str:
        parts = [
            # Function signature
            f"def {func.name}({self._format_parameters(func.parameters)}):",
            
            # Docstring
            func.docstring or "",
            
            # Class context if method
            f"in class {context.containing_class}" if context.containing_class else "",
            
            # Module context
            f"in module {context.module_name}",
            
            # Related functions
            f"calls: {', '.join(func.calls)}" if func.calls else "",
            
            # Framework context
            f"framework: {context.framework}" if context.framework else ""
        ]
        
        return " ".join(filter(None, parts))
```

### 6. Search Engine Architecture

```python
# search/search_engine.py
class CodeSearchEngine:
    def __init__(self):
        self.vector_store = QdrantVectorStore()
        self.graph_db = Neo4jGraphDB()
        self.query_processor = QueryProcessor()
        self.result_ranker = ResultRanker()
    
    async def search(self, query: str, context: SearchContext) -> SearchResults:
        """Main search entry point."""
        # 1. Process and understand the query
        processed_query = await self.query_processor.process(query, context)
        
        # 2. Execute multi-modal search
        search_results = await self._execute_multi_modal_search(processed_query)
        
        # 3. Rank and filter results
        ranked_results = await self.result_ranker.rank(search_results, processed_query)
        
        # 4. Add explanations and context
        enhanced_results = await self._enhance_results(ranked_results, context)
        
        return enhanced_results
    
    async def _execute_multi_modal_search(self, query: ProcessedQuery) -> List[SearchResult]:
        """Execute search across multiple modalities."""
        results = []
        
        # Vector similarity search
        if query.intent in [QueryIntent.SEMANTIC, QueryIntent.FUNCTIONAL]:
            vector_results = await self._vector_search(query)
            results.extend(vector_results)
        
        # Graph traversal search
        if query.intent in [QueryIntent.STRUCTURAL, QueryIntent.RELATIONSHIP]:
            graph_results = await self._graph_search(query)
            results.extend(graph_results)
        
        # Pattern-based search
        if query.intent == QueryIntent.PATTERN:
            pattern_results = await self._pattern_search(query)
            results.extend(pattern_results)
        
        # Exact match search
        if query.has_exact_terms:
            exact_results = await self._exact_search(query)
            results.extend(exact_results)
        
        return self._deduplicate_results(results)

# search/query_processor.py
class QueryProcessor:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = QueryEntityExtractor()
        self.query_expander = QueryExpander()
    
    async def process(self, query: str, context: SearchContext) -> ProcessedQuery:
        """Process raw query into structured search parameters."""
        
        # Classify query intent
        intent = await self.intent_classifier.classify(query)
        
        # Extract entities and constraints
        entities = await self.entity_extractor.extract(query)
        constraints = self._extract_constraints(query, context)
        
        # Expand query with synonyms and related terms
        expanded_terms = await self.query_expander.expand(query, context)
        
        return ProcessedQuery(
            original_query=query,
            intent=intent,
            entities=entities,
            constraints=constraints,
            expanded_terms=expanded_terms,
            context=context
        )

class IntentClassifier:
    """Classify the intent of code search queries."""
    
    INTENT_PATTERNS = {
        QueryIntent.SEMANTIC: [
            r"find.*(?:function|method|class).*(?:that|which)",
            r"show.*(?:code|implementation).*for",
            r"(?:how to|example of).*",
        ],
        QueryIntent.STRUCTURAL: [
            r"(?:all|list).*(?:classes|functions).*(?:inherit|extend)",
            r"(?:find|show).*(?:subclasses|implementations)",
            r"what.*(?:calls|uses|imports)",
        ],
        QueryIntent.PATTERN: [
            r"(?:singleton|factory|observer|decorator).*pattern",
            r"design pattern.*",
            r"show.*pattern.*implementation",
        ],
        QueryIntent.FUNCTIONAL: [
            r"(?:authentication|logging|validation|error handling)",
            r"(?:database|api|http).*(?:connection|request|response)",
            r"(?:parse|process|handle).*",
        ]
    }
    
    async def classify(self, query: str) -> QueryIntent:
        query_lower = query.lower()
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        # Default to semantic search
        return QueryIntent.SEMANTIC
```

### 7. Result Ranking System

```python
# ranking/result_ranker.py
class ResultRanker:
    def __init__(self):
        self.relevance_scorer = RelevanceScorer()
        self.quality_scorer = QualityScorer()
        self.context_scorer = ContextScorer()
    
    async def rank(self, results: List[SearchResult], query: ProcessedQuery) -> List[RankedResult]:
        """Rank search results using multiple scoring factors."""
        
        ranked_results = []
        for result in results:
            # Calculate different score components
            relevance_score = await self.relevance_scorer.score(result, query)
            quality_score = await self.quality_scorer.score(result)
            context_score = await self.context_scorer.score(result, query.context)
            
            # Combine scores with weights
            final_score = (
                0.5 * relevance_score +
                0.3 * quality_score +
                0.2 * context_score
            )
            
            ranked_results.append(RankedResult(
                result=result,
                final_score=final_score,
                relevance_score=relevance_score,
                quality_score=quality_score,
                context_score=context_score,
                explanation=self._generate_explanation(result, query)
            ))
        
        # Sort by final score
        ranked_results.sort(key=lambda x: x.final_score, reverse=True)
        return ranked_results

class RelevanceScorer:
    """Score results based on relevance to query."""
    
    def __init__(self):
        self.embedder = CodeEmbedder()
    
    async def score(self, result: SearchResult, query: ProcessedQuery) -> float:
        # Vector similarity score
        query_embedding = self.embedder.embed_query(query.original_query)
        result_embedding = result.embedding
        vector_similarity = cosine_similarity(query_embedding, result_embedding)
        
        # Exact term matching score
        exact_match_score = self._calculate_exact_matches(result, query)
        
        # Entity matching score
        entity_match_score = self._calculate_entity_matches(result, query)
        
        # Combine scores
        return (
            0.4 * vector_similarity +
            0.3 * exact_match_score +
            0.3 * entity_match_score
        )

class QualityScorer:
    """Score results based on code quality indicators."""
    
    async def score(self, result: SearchResult) -> float:
        scores = []
        
        # Documentation score
        if hasattr(result.entity, 'docstring') and result.entity.docstring:
            doc_score = min(len(result.entity.docstring) / 100, 1.0)
            scores.append(doc_score)
        
        # Complexity score (lower complexity = higher score)
        if hasattr(result.entity, 'complexity'):
            complexity_score = max(0, 1.0 - (result.entity.complexity / 20))
            scores.append(complexity_score)
        
        # Naming score (descriptive names)
        naming_score = self._score_naming_quality(result.entity.name)
        scores.append(naming_score)
        
        # Test coverage score (if available)
        test_coverage = getattr(result.entity, 'test_coverage', 0.5)
        scores.append(test_coverage)
        
        return sum(scores) / len(scores) if scores else 0.5
```

### 8. API Layer

```python
# api/main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from typing import List, Optional

app = FastAPI(title="Code RAG API", version="1.0.0")
security = HTTPBearer()

@app.post("/api/v1/code/ingest", response_model=IngestionResponse)
async def ingest_code(
    request: IngestionRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(security)
):
    """Ingest code repository or files."""
    try:
        # Validate request
        if not request.repository_url and not request.files:
            raise HTTPException(400, "Either repository_url or files must be provided")
        
        # Start background ingestion task
        task_id = generate_task_id()
        background_tasks.add_task(
            process_ingestion,
            task_id,
            request
        )
        
        return IngestionResponse(
            task_id=task_id,
            status="started",
            message="Ingestion started successfully"
        )
    
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {str(e)}")

@app.post("/api/v1/code/search", response_model=SearchResponse)
async def search_code(
    request: SearchRequest,
    token: str = Depends(security)
):
    """Search for code using natural language or structured queries."""
    try:
        search_engine = get_search_engine()
        
        # Build search context
        context = SearchContext(
            language=request.language,
            project_context=request.project_context,
            user_preferences=request.user_preferences
        )
        
        # Execute search
        results = await search_engine.search(request.query, context)
        
        return SearchResponse(
            query=request.query,
            results=[result.to_dict() for result in results],
            total_results=len(results),
            search_time_ms=results.search_time_ms,
            suggestions=results.suggestions
        )
    
    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")

@app.get("/api/v1/code/analyze/{entity_id}", response_model=AnalysisResponse)
async def analyze_code_entity(
    entity_id: str,
    include_relationships: bool = True,
    include_patterns: bool = True,
    token: str = Depends(security)
):
    """Analyze a specific code entity."""
    try:
        analyzer = get_code_analyzer()
        
        analysis = await analyzer.analyze_entity(
            entity_id,
            include_relationships=include_relationships,
            include_patterns=include_patterns
        )
        
        return AnalysisResponse(
            entity_id=entity_id,
            analysis=analysis.to_dict()
        )
    
    except EntityNotFoundError:
        raise HTTPException(404, f"Entity {entity_id} not found")
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")

# API Models
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class IngestionRequest(BaseModel):
    repository_url: Optional[str] = None
    files: Optional[List[str]] = None
    language: Optional[str] = None
    project_name: str
    include_tests: bool = True
    include_docs: bool = True

class SearchRequest(BaseModel):
    query: str
    language: Optional[str] = None
    max_results: int = 20
    include_explanations: bool = True
    project_context: Optional[Dict[str, Any]] = None
    user_preferences: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    search_time_ms: float
    suggestions: Optional[List[str]] = None
```

## Performance Optimizations

### 1. Caching Strategy

```python
# caching/cache_manager.py
import redis
from typing import Any, Optional
import pickle
import hashlib

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour
    
    def cache_search_results(self, query: str, context: dict, results: Any, ttl: int = None):
        """Cache search results with query and context as key."""
        cache_key = self._generate_cache_key("search", query, context)
        serialized_results = pickle.dumps(results)
        self.redis_client.setex(cache_key, ttl or self.default_ttl, serialized_results)
    
    def get_cached_search_results(self, query: str, context: dict) -> Optional[Any]:
        """Retrieve cached search results."""
        cache_key = self._generate_cache_key("search", query, context)
        cached_data = self.redis_client.get(cache_key)
        return pickle.loads(cached_data) if cached_data else None
    
    def _generate_cache_key(self, prefix: str, *args) -> str:
        """Generate deterministic cache key."""
        content = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(content.encode()).hexdigest()
```

### 2. Database Optimizations

```python
# database/optimizations.py
class DatabaseOptimizer:
    """Optimize database queries and indexes."""
    
    def create_indexes(self):
        """Create optimized indexes for common queries."""
        indexes = [
            # Function search indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_function_name_trgm ON functions USING gin(name gin_trgm_ops)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_function_language ON functions(language)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_function_complexity ON functions(complexity)",
            
            # Class search indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_class_name_trgm ON classes USING gin(name gin_trgm_ops)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_class_patterns ON classes USING gin(design_patterns)",
            
            # Relationship indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_relationships_source ON relationships(source_entity_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_relationships_target ON relationships(target_entity_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_relationships_type ON relationships(relationship_type)",
        ]
        
        for index_sql in indexes:
            self.execute_sql(index_sql)
    
    def optimize_vector_search(self):
        """Optimize vector similarity search."""
        # Configure Qdrant for optimal performance
        qdrant_config = {
            "hnsw_config": {
                "m": 16,
                "ef_construct": 100,
                "full_scan_threshold": 10000
            },
            "quantization_config": {
                "scalar": {
                    "type": "int8",
                    "always_ram": True
                }
            }
        }
        return qdrant_config
```

This technical architecture provides a solid foundation for building a production-ready Code RAG system that can understand, index, and retrieve code intelligently across multiple programming languages and paradigms. 