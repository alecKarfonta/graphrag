#!/bin/bash

# Graph RAG System Startup Script

echo "🚀 Starting Graph RAG System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating example .env file..."
    cat > .env << EOF
# Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Vector Database
QDRANT_URL=http://localhost:6333

# LLM Configuration
ANTHROPIC_API_KEY=your_claude_api_key_here

# Optional: OpenAI (if you want to use GPT-4 as fallback)
OPENAI_API_KEY=your_openai_api_key_here

# Web Scraping
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
EOF
    echo "📝 Please edit .env file with your API keys before starting the system."
    echo "   Required: ANTHROPIC_API_KEY"
    echo "   Optional: OPENAI_API_KEY, FIRECRAWL_API_KEY"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Function to check if services are ready
check_services() {
    echo "🔍 Checking if services are ready..."
    
    # Check Neo4j
    if curl -s http://localhost:7474 > /dev/null; then
        echo "✅ Neo4j is ready"
    else
        echo "⏳ Neo4j is starting..."
        return 1
    fi
    
    # Check Qdrant
    if curl -s http://localhost:6333/collections > /dev/null; then
        echo "✅ Qdrant is ready"
    else
        echo "⏳ Qdrant is starting..."
        return 1
    fi
    
    # Check API
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API is ready"
    else
        echo "⏳ API is starting..."
        return 1
    fi
    
    return 0
}

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
for i in {1..30}; do
    if check_services; then
        break
    fi
    sleep 10
done

# Final check
if check_services; then
    echo ""
    echo "🎉 Graph RAG System is ready!"
    echo ""
    echo "📊 Services:"
    echo "   Frontend:     http://localhost:3000"
    echo "   API:          http://localhost:8000"
    echo "   Neo4j:        http://localhost:7474"
    echo "   Qdrant:       http://localhost:6333"
    echo "   Redis:        localhost:6379"
    echo ""
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "🛑 To stop the system: docker-compose down"
    echo "📝 To view logs: docker-compose logs -f"
else
    echo "❌ Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi 