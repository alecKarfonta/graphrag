# Graph RAG System

An advanced Retrieval-Augmented Generation (RAG) system that leverages a knowledge graph to provide context-rich, accurate answers from a corpus of documents. This project integrates cutting-edge NLP models for entity and relationship extraction, graph-based data storage, and a hybrid retrieval system to power its question-answering capabilities.

## Key Features

- **Intelligent Document Processing**: Ingests and processes multiple document formats (PDF, DOCX, TXT, etc.), using semantic chunking for meaningful data segmentation.
- **High-Fidelity Extraction**: Utilizes the GLiNER model for precise entity and relationship extraction, forming the backbone of the knowledge graph.
- **Knowledge Graph Construction**: Automatically builds and maintains a robust knowledge graph in Neo4j, capturing complex relationships within the source data.
- **Hybrid Retrieval System**: Combines semantic vector search (via Qdrant) and graph-based traversal to retrieve the most relevant context for a given query.
- **Interactive Frontend**: A React-based user interface for document management, knowledge graph exploration, and interacting with the RAG system.
- **Containerized Deployment**: Fully containerized with Docker for easy setup, consistent development, and scalable deployment.

## System Architecture

The system is composed of three main services orchestrated by Docker Compose:

1.  **Backend (FastAPI)**: A Python-based API that exposes all the core functionalities, including document ingestion, entity extraction, graph construction, and the RAG pipeline.
2.  **Frontend (React)**: A modern, responsive user interface for interacting with the backend.
3.  **Databases**:
    *   **Neo4j**: A graph database used to store the knowledge graph of entities and relationships.
    *   **Qdrant**: A vector database used for efficient semantic search over document chunks.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- An Anthropic API key (for the LLM-based response generation)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd graphrag
    ```

2.  **Configure Environment Variables**
    Create a `.env` file in the project root by copying the example:
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file and add your Anthropic API key:
    ```
    # .env
    ANTHROPIC_API_KEY="your_anthropic_api_key_here"
    ```

3.  **Launch the System**
    ```bash
    docker compose up -d --build
    ```
    This command will build the Docker images and start all the services in the background.

### Accessing the Services

- **Application Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000/docs`
- **Neo4j Browser**: `http://localhost:7474`
- **Qdrant Dashboard**: `http://localhost:6333/dashboard`

## Usage

1.  **Upload Documents**: Navigate to the web interface and upload your documents. The system will process them, extract entities, and build the knowledge graph automatically.
2.  **Explore the Graph**: Use the graph visualization tool to explore the extracted entities and their relationships.
3.  **Ask Questions**: Use the query interface to ask natural language questions. The system will use the RAG pipeline to retrieve relevant information and generate a comprehensive answer.

## Testing

The project includes a suite of tests to ensure the reliability of its components. The tests are organized into `unit`, `integration`, and `e2e` (end-to-end) categories.

To run the tests, execute the test scripts located in the `backend/` directory from within the `api` container:

```bash
# Example: Run the end-to-end test for the extraction pipeline
docker compose exec api python test_entity_extraction.py
```

## Project Structure

The repository is organized into the following directories:

```
.
├── backend/            # FastAPI application, core logic, and models
├── docs/               # Project documentation files
├── frontend/           # React frontend application
├── scripts/            # Utility and demonstration scripts
├── tests/              # Unit, integration, and e2e tests
│   ├── data/           # Test data and documents
│   ├── e2e/
│   ├── integration/
│   └── unit/
├── .env.example        # Example environment variables
├── .gitignore          # Files and directories to be ignored by Git
├── docker-compose.yml  # Docker Compose configuration
└── README.md           # This file
```

## Troubleshooting

- **Container Issues**: Use `docker compose ps` to check the status of all running containers and `docker compose logs <service_name>` (e.g., `api`, `frontend`) to view their logs.
- **Dependency Problems**: If you encounter issues after adding new packages, you may need to rebuild your containers: `docker compose up -d --build`. 