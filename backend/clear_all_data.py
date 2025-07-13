#!/usr/bin/env python3
"""
Clear all data from vector store and knowledge graph
"""

import os
import sys
import logging

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hybrid_retriever import HybridRetriever
from knowledge_graph_builder import KnowledgeGraphBuilder

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clear_all_data():
    """Clear all data from vector store and knowledge graph."""
    logger.info("🧹 Starting data cleanup...")
    
    # Get environment variables
    qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    
    logger.info(f"🔧 Using Qdrant URL: {qdrant_url}")
    logger.info(f"🔧 Using Neo4j URI: {neo4j_uri}")
    
    # Clear vector store
    logger.info("🔄 Clearing vector store...")
    try:
        retriever = HybridRetriever(qdrant_url=qdrant_url)
        retriever.clear_all()
        logger.info("✅ Vector store cleared successfully")
    except Exception as e:
        logger.error(f"❌ Failed to clear vector store: {e}")
        return False
    
    # Clear knowledge graph
    logger.info("🔄 Clearing knowledge graph...")
    try:
        kg_builder = KnowledgeGraphBuilder(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password
        )
        kg_builder.clear_knowledge_graph()
        logger.info("✅ Knowledge graph cleared successfully")
    except Exception as e:
        logger.error(f"❌ Failed to clear knowledge graph: {e}")
        return False
    
    logger.info("✅ All data cleared successfully!")
    return True

if __name__ == "__main__":
    try:
        success = clear_all_data()
        if success:
            print("\n🎉 All data has been successfully cleared!")
            print("   - Vector store (Qdrant): ✅ Cleared")
            print("   - Knowledge graph (Neo4j): ✅ Cleared")
        else:
            print("\n❌ Data clearing failed. Check the logs above.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        print(f"\n❌ Critical error: {e}")
        sys.exit(1) 