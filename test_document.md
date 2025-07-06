# Machine Learning and Artificial Intelligence

## Introduction

Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.

## Types of Machine Learning

### Supervised Learning
Supervised learning involves training a model on labeled data. The algorithm learns to map input data to known outputs. Examples include:
- Classification: Categorizing emails as spam or not spam
- Regression: Predicting house prices based on features

### Unsupervised Learning
Unsupervised learning finds hidden patterns in data without labeled responses. Examples include:
- Clustering: Grouping customers by purchasing behavior
- Dimensionality reduction: Reducing data complexity

### Deep Learning
Deep learning is a subset of machine learning that uses neural networks with multiple layers. It excels at:
- Image recognition
- Natural language processing
- Speech recognition

## Applications

Machine learning has numerous applications across industries:
- Healthcare: Disease diagnosis and drug discovery
- Finance: Fraud detection and risk assessment
- Transportation: Self-driving cars and route optimization
- Entertainment: Recommendation systems

## Challenges

Key challenges in machine learning include:
- Data quality and quantity
- Model interpretability
- Bias and fairness
- Computational resources

## Future Directions

The future of machine learning includes:
- Federated learning for privacy
- Automated machine learning (AutoML)
- Edge computing for real-time processing
- Integration with quantum computing 

# GraphRAG System Overview

## Introduction

GraphRAG is an advanced document processing and knowledge graph system that combines entity extraction, relationship discovery, and intelligent querying capabilities.

## Core Features

### Entity Extraction
- **Named Entity Recognition (NER)**: Identifies people, organizations, locations, and other entities
- **Enhanced Extraction**: Uses SpanBERT, dependency parsing, and entity linking
- **Multi-method Ensemble**: Combines multiple extraction methods for better accuracy

### Relationship Discovery
- **GLiNER Integration**: Advanced relationship extraction using GLiNER model
- **Dependency Parsing**: Syntactic relationship extraction
- **Knowledge Graph Building**: Automatic construction of entity-relationship graphs

### Query Processing
- **Hybrid Retrieval**: Combines vector search and graph traversal
- **Advanced Reasoning**: Multi-hop, causal, and comparative reasoning
- **Enhanced Query Processing**: Context-aware query expansion and processing

## Architecture

### Backend Components
- **FastAPI**: RESTful API framework
- **Neo4j**: Knowledge graph database
- **Qdrant**: Vector database for semantic search
- **Docker**: Containerized deployment

### Document Processing
- **Multi-format Support**: PDF, DOCX, TXT, HTML, CSV, JSON, and now Markdown
- **Chunking**: Intelligent text chunking with overlap
- **Metadata Extraction**: Automatic extraction of document metadata

## Usage Examples

### Document Ingestion
```bash
curl -X POST "http://localhost:8000/ingest-documents" \
  -F "files=@document.pdf" \
  -F "files=@document.md"
```

### Entity Extraction
```bash
curl -X POST "http://localhost:8000/extract-entities-relations-enhanced" \
  -d "text=Microsoft was founded by Bill Gates" \
  -d "domain=technology"
```

### Query Processing
```bash
curl -X POST "http://localhost:8000/enhanced-query" \
  -d "query=What connects Microsoft to Bill Gates?"
```

## Advanced Features

### Knowledge Graph Enhancement
- **Entity Linking**: Connect entities to external knowledge bases
- **Entity Disambiguation**: Resolve entity name conflicts
- **Graph Reasoning**: Advanced graph traversal and reasoning

### Query Enhancement
- **Graph-based Expansion**: Expand queries using knowledge graph structure
- **Relationship-aware Search**: Consider entity relationships in search
- **Multi-hop Reasoning**: Follow multiple relationship paths

## Performance Metrics

The system provides comprehensive performance monitoring:
- **Query Response Time**: Average response times for different query types
- **Extraction Quality**: Precision and recall for entity/relationship extraction
- **Knowledge Graph Statistics**: Node and relationship counts
- **System Health**: Overall system status and component health

## Future Enhancements

### Planned Features
- **Temporal Relationships**: Time-aware relationship modeling
- **Advanced Analytics**: Graph analytics and visualization
- **Real-time Updates**: Live knowledge graph updates
- **Multimodal Support**: Image and audio processing

### Performance Optimization
- **Caching**: Intelligent caching for frequently accessed data
- **Parallel Processing**: Multi-threaded document processing
- **Distributed Processing**: Scalable architecture for large datasets 