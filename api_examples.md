# Enhanced GraphRAG API Examples

This document provides comprehensive examples for all advanced endpoints in the GraphRAG system.

## 🚀 Enhanced Query Processing

### Endpoint: `POST /api/enhanced-query`

**Purpose**: Process queries with advanced reasoning, intent analysis, and multi-strategy search.

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/enhanced-query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the difference between supervised and unsupervised learning?"}'
```

**Example Response**:
```json
{
  "query": "What is the difference between supervised and unsupervised learning?",
  "answer": "Supervised learning and unsupervised learning are two broad categories...",
  "sources": [],
  "reasoning_paths": [],
  "confidence": 0.95,
  "search_strategy": {
    "components": [
      {
        "type": "vector_search",
        "priority": 2,
        "query": "COMPARATIVE",
        "confidence": 0.7
      },
      {
        "type": "graph_traversal",
        "priority": 3,
        "entities": ["supervised learning", "unsupervised learning"],
        "confidence": 0.8
      }
    ],
    "confidence": 0.75,
    "explanation": "Query intent: COMPARATIVE. Strategy: Searching for semantically similar content + Traversing knowledge graph for direct relationships"
  },
  "follow_up_suggestions": [
    "What are the key differences between these entities?",
    "How do these entities compare in terms of performance?",
    "What are the advantages and disadvantages of each?"
  ],
  "explanation": "Query Intent: COMPARATIVE (confidence: 0.95)\nComplexity Level: medium\n\nSearch Strategy: Query intent: COMPARATIVE. Strategy: Searching for semantically similar content + Traversing knowledge graph for direct relationships"
}
```

## 🧠 Advanced Reasoning

### Endpoint: `POST /api/advanced-reasoning`

**Purpose**: Perform advanced reasoning on queries using multi-hop, causal, and comparative analysis.

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/advanced-reasoning" \
  -H "Content-Type: application/json" \
  -d '{"query": "How does machine learning compare to deep learning?"}'
```

**Example Response**:
```json
{
  "query": "How does machine learning compare to deep learning?",
  "entities": ["machine learning", "deep learning"],
  "reasoning_paths": [
    {
      "path_type": "comparative",
      "entities": ["machine learning", "deep learning"],
      "relationships": ["is_subset_of", "uses"],
      "confidence": 0.85,
      "evidence": ["Deep learning is a subset of machine learning"],
      "reasoning_chain": ["machine learning is broader", "deep learning uses neural networks"]
    }
  ],
  "explanation": "Found 1 reasoning path comparing machine learning and deep learning",
  "total_paths": 1
}
```

## 🔗 Causal Reasoning

### Endpoint: `POST /api/causal-reasoning`

**Purpose**: Find cause-effect relationships in the knowledge graph.

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/causal-reasoning" \
  -H "Content-Type: application/json" \
  -d '{"query": "What causes climate change?"}'
```

**Example Response**:
```json
{
  "query": "What causes climate change?",
  "entities": ["climate change"],
  "causal_chains": [
    {
      "path_type": "causal",
      "entities": ["greenhouse gases", "climate change"],
      "relationships": ["CAUSES"],
      "confidence": 0.9,
      "evidence": ["Greenhouse gases trap heat in the atmosphere"],
      "reasoning_chain": ["emissions increase", "temperature rises", "climate changes"]
    }
  ],
  "total_chains": 1
}
```

## ⚖️ Comparative Reasoning

### Endpoint: `POST /api/comparative-reasoning`

**Purpose**: Compare entities and find similarities/differences.

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/comparative-reasoning" \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare supervised and unsupervised learning"}'
```

**Example Response**:
```json
{
  "query": "Compare supervised and unsupervised learning",
  "entities": ["supervised learning", "unsupervised learning"],
  "comparisons": [
    {
      "path_type": "comparative",
      "entities": ["supervised learning", "unsupervised learning"],
      "relationships": ["differs_from"],
      "confidence": 0.88,
      "evidence": ["Supervised uses labeled data", "Unsupervised uses unlabeled data"],
      "reasoning_chain": ["data requirements differ", "objectives differ", "applications differ"]
    }
  ],
  "total_comparisons": 1
}
```

## 🔄 Multi-Hop Reasoning

### Endpoint: `POST /api/multi-hop-reasoning`

**Purpose**: Find complex relationships across multiple entities.

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/multi-hop-reasoning" \
  -H "Content-Type: application/json" \
  -d '{"query": "How does AI relate to machine learning?", "max_hops": 3}'
```

**Example Response**:
```json
{
  "query": "How does AI relate to machine learning?",
  "entities": ["AI", "machine learning"],
  "max_hops": 3,
  "reasoning_paths": [
    {
      "path_type": "multi_hop",
      "entities": ["AI", "machine learning", "deep learning"],
      "relationships": ["includes", "is_subset_of"],
      "confidence": 0.92,
      "evidence": ["AI includes machine learning", "Machine learning includes deep learning"],
      "reasoning_chain": ["AI is broad field", "ML is subset of AI", "DL is subset of ML"]
    }
  ],
  "total_paths": 1
}
```

## 📊 Query Complexity Analysis

### Endpoint: `POST /api/query-complexity-analysis`

**Purpose**: Analyze query complexity and determine reasoning requirements.

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/query-complexity-analysis" \
  -H "Content-Type: application/json" \
  -d '{"query": "How does machine learning cause improvements in technology?"}'
```

**Example Response**:
```json
{
  "query": "How does machine learning cause improvements in technology?",
  "primary_reasoning": "causal",
  "detected_patterns": ["causal", "multi_hop"],
  "complexity_level": "high",
  "requires_multi_hop": true
}
```

## 🎯 Query Intent Analysis

### Endpoint: `POST /api/analyze-query-intent`

**Purpose**: Analyze the intent and type of a user query.

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/analyze-query-intent" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the relationship between AI and machine learning?"}'
```

**Example Response**:
```json
{
  "intent_type": "COMPARATIVE",
  "confidence": 0.95,
  "entities": ["AI", "machine learning"],
  "reasoning_required": true,
  "search_strategy": "hybrid",
  "complexity_level": "medium",
  "follow_up_questions": [
    "How do they differ in practice?",
    "What are the key applications of each?"
  ]
}
```

## 🔍 Entity Extraction

### Endpoint: `POST /extract-entities-relations`

**Purpose**: Extract entities and relationships from text.

**Example Request**:
```bash
curl -X POST "http://localhost:8000/extract-entities-relations" \
  -H "Content-Type: application/json" \
  -d '{"text": "Deep learning is a subset of machine learning that uses neural networks.", "domain": "technology"}'
```

**Example Response**:
```json
{
  "text": "Deep learning is a subset of machine learning that uses neural networks.",
  "domain": "technology",
  "entities": [
    {
      "name": "neural networks",
      "type": "COMPONENT",
      "description": "Extracted by GLiNER model (confidence: 0.623)",
      "confidence": 0.6234431862831116,
      "metadata": {
        "domain": "technology",
        "ner_source": "gliner_model",
        "original_ner_type": "component"
      }
    }
  ],
  "relationships": [],
  "claims": [],
  "entity_count": 1,
  "relationship_count": 0,
  "extraction_method": "integrated"
}
```

## 📈 Performance Monitoring

### Endpoint: `GET /knowledge-graph/stats`

**Purpose**: Get knowledge graph statistics.

**Example Request**:
```bash
curl -X GET "http://localhost:8000/knowledge-graph/stats"
```

**Example Response**:
```json
{
  "nodes": 4,
  "edges": 0,
  "density": 0,
  "average_clustering": 0.0,
  "connected_components": 4,
  "average_shortest_path": null
}
```

## 🏥 Health Check

### Endpoint: `GET /health`

**Purpose**: Check system health.

**Example Request**:
```bash
curl -X GET "http://localhost:8000/health"
```

**Example Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-06T04:31:54.662829"
}
```

## 📋 Usage Guidelines

### Best Practices:

1. **Query Formulation**: Use clear, specific queries for better results
2. **Domain Specification**: Include domain context when extracting entities
3. **Error Handling**: Always check response status codes
4. **Performance**: Monitor response times for optimization

### Common Patterns:

1. **Factual Queries**: "What is X?" → Use enhanced query processing
2. **Comparative Queries**: "Compare X and Y" → Use comparative reasoning
3. **Causal Queries**: "What causes X?" → Use causal reasoning
4. **Complex Queries**: "How does X relate to Y?" → Use multi-hop reasoning

### Error Handling:

```python
import requests

try:
    response = requests.post("http://localhost:8000/api/enhanced-query", 
                           params={"query": "What is machine learning?"})
    
    if response.status_code == 200:
        result = response.json()
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"Connection error: {e}")
```

## 🚀 Performance Tips

1. **Batch Processing**: Use batch endpoints for multiple queries
2. **Caching**: Cache frequently requested results
3. **Async Processing**: Use async requests for better performance
4. **Monitoring**: Track response times and success rates

## 📊 Performance Benchmarks

Based on recent testing:

- **Enhanced Query Processing**: ~8.8s average response time
- **Advanced Reasoning**: ~0.3s average response time
- **Entity Extraction**: ~0.4s average response time
- **Query Analysis**: ~2.0s average response time
- **Overall Success Rate**: 100%

## 🔧 Troubleshooting

### Common Issues:

1. **Empty Reasoning Results**: Knowledge graph may be empty
2. **Slow Response Times**: Check system resources
3. **Entity Extraction Issues**: Verify text format and domain
4. **Connection Errors**: Ensure all services are running

### Debug Steps:

1. Check health endpoint
2. Verify knowledge graph has data
3. Test entity extraction separately
4. Monitor system logs
5. Check service dependencies 