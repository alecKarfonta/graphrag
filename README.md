# Graph RAG System

A state-of-the-art Graph RAG (Retrieval-Augmented Generation) system that combines knowledge graphs with vector search to provide superior question-answering capabilities for niche domains.

## 🚀 Features

- **Multi-format Document Processing**: PDF, DOCX, TXT, HTML, CSV, JSON
- **Intelligent Entity Extraction**: LLM-powered entity and relationship extraction
- **Knowledge Graph Construction**: Automatic graph building with Neo4j
- **Hybrid Search**: Vector search + graph traversal for comprehensive retrieval
- **Interactive Visualization**: Real-time knowledge graph visualization
- **RAG Integration**: LLM-powered answer generation from retrieved context
- **Containerized Deployment**: Docker Compose setup for easy deployment

## 🏗️ Architecture

### Core Components

1. **Backend (FastAPI)**
   - Document processing pipeline
   - Entity extraction with Claude LLM
   - Knowledge graph construction
   - Hybrid search engine
   - RAG answer generation

2. **Frontend (React + TypeScript)**
   - Interactive document upload
   - Real-time knowledge graph visualization
   - Query interface with RAG responses
   - Document management

3. **Databases**
   - **Neo4j**: Knowledge graph storage
   - **Qdrant**: Vector database for semantic search

4. **LLM Integration**
   - **Claude 3 Sonnet**: Entity extraction and RAG generation

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, LangChain
- **Frontend**: React, TypeScript, Tailwind CSS
- **Databases**: Neo4j, Qdrant
- **LLM**: Anthropic Claude 3 Sonnet
- **Deployment**: Docker, Docker Compose

## 📋 Prerequisites

- Docker and Docker Compose
- Anthropic API key for Claude LLM

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd graphrag
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Anthropic API Key (required for entity extraction and RAG)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Custom database URLs
NEO4J_URI=bolt://localhost:7687
QDRANT_URL=http://localhost:6333
```

### 3. Start the System

```bash
docker compose up -d
```

This will start:
- **API Server**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **Neo4j**: http://localhost:7474
- **Qdrant**: http://localhost:6333

### 4. Access the Application

Open your browser and navigate to http://localhost:3000

## 📖 Usage

### 1. Upload Documents

1. Go to the **Document Manager** tab
2. Click "Upload Documents" or drag and drop files
3. Supported formats: PDF, DOCX, TXT, HTML, CSV, JSON
4. The system will automatically:
   - Process and chunk documents
   - Extract entities and relationships
   - Build the knowledge graph
   - Add to vector store

### 2. Explore the Knowledge Graph

1. Go to the **Knowledge Graph** tab
2. View the interactive graph visualization
3. See entities (nodes) and relationships (edges)
4. Use the refresh button to update the view

### 3. Ask Questions

1. Go to the **Query Interface** tab
2. Type your question in natural language
3. The system will:
   - Search through documents using hybrid retrieval
   - Generate comprehensive answers using RAG
   - Show relevant sources and entities

## 🔧 Configuration

### Entity Types

The system supports domain-specific entity types:

- **General**: PERSON, ORGANIZATION, LOCATION, CONCEPT, PROCESS
- **Technical**: COMPONENT, SPECIFICATION, PROCEDURE, SYSTEM, INTERFACE
- **Automotive**: COMPONENT, SPECIFICATION, PROCEDURE, MAINTENANCE_ITEM, SYMPTOM, SOLUTION
- **Medical**: SYMPTOM, DIAGNOSIS, TREATMENT, MEDICATION, PROCEDURE
- **Legal**: LAW, REGULATION, CASE, PRECEDENT, JURISDICTION

### Relationship Types

- **General**: RELATES_TO, PART_OF, CONTAINS, CAUSES, REQUIRES
- **Technical**: CONNECTS_TO, DEPENDS_ON, IMPLEMENTS, CONFIGURES, MONITORS
- **Automotive**: PART_OF, CONNECTS_TO, REQUIRES, CAUSES, FIXES, SCHEDULED_AT

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure all containers are running: `docker compose ps`
   - Check logs: `docker compose logs api`

2. **Entity Extraction Hanging**
   - The system now processes chunks in batches with timeouts
   - Check API logs for progress updates
   - Large documents may take several minutes

3. **Knowledge Graph Empty**
   - Ensure documents have been uploaded successfully
   - Check that entity extraction completed without errors
   - Verify Neo4j connection

### Logs and Debugging

```bash
# View all container logs
docker compose logs

# View specific service logs
docker compose logs api
docker compose logs frontend
docker compose logs neo4j
docker compose logs qdrant

# Rebuild containers
docker compose up -d --build
```

## 🔄 Development

### Project Structure

```
graphrag/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main API server
│   ├── entity_extractor.py # LLM-based entity extraction
│   ├── knowledge_graph_builder.py # Neo4j graph operations
│   ├── hybrid_retriever.py # Vector + graph search
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.tsx        # Main application
│   │   └── index.css      # Styles
│   └── package.json       # Node.js dependencies
├── docker-compose.yml      # Container orchestration
├── .env                    # Environment variables
└── README.md              # This file
```

### Adding New Features

1. **Backend Changes**
   - Modify Python files in `backend/`
   - Rebuild: `docker compose up -d --build api`

2. **Frontend Changes**
   - Modify React files in `frontend/src/`
   - Rebuild: `docker compose up -d --build frontend`

3. **Database Changes**
   - Modify Neo4j schema in `knowledge_graph_builder.py`
   - Modify Qdrant schema in `hybrid_retriever.py`

## 📊 Performance

### Optimization Features

- **Batch Processing**: Entity extraction processes chunks in batches
- **Timeout Handling**: 30-second timeout per chunk prevents hanging
- **Error Recovery**: Continues processing even if some chunks fail
- **Progress Logging**: Real-time progress updates during processing

### Scaling Considerations

- **Large Documents**: Process in smaller chunks for better performance
- **API Limits**: Monitor Anthropic API usage and rate limits
- **Memory Usage**: Neo4j and Qdrant can be memory-intensive for large graphs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m 'Add feature'`
6. Push: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude LLM API
- **Neo4j** for graph database
- **Qdrant** for vector database
- **FastAPI** for the web framework
- **React** for the frontend framework

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Open an issue on GitHub with detailed information

---

**Happy Graph RAG-ing! 🕸️🚀** 