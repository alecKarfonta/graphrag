#!/bin/bash

# GraphRAG Restore Script
# This script restores data from a backup

set -e

if [ $# -eq 0 ]; then
    echo "❌ Error: Please provide a backup name"
    echo "Usage: $0 <backup_name>"
    echo "Example: $0 graphrag_backup_20241201_143022"
    exit 1
fi

BACKUP_NAME=$1
BACKUP_DIR="./backups"
BACKUP_FILE="$BACKUP_DIR/${BACKUP_NAME}.tar.gz"

echo "🚀 Starting GraphRAG restore..."
echo "📦 Backup name: $BACKUP_NAME"
echo "📁 Backup file: $BACKUP_FILE"

# Check if backup exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Backup file not found: $BACKUP_FILE"
    echo "Available backups:"
    ls -la "$BACKUP_DIR"/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

    # Stop services before restore
    echo "🛑 Stopping GraphRAG services..."
    docker compose down

# Extract backup
echo "📦 Extracting backup..."
mkdir -p "$BACKUP_DIR/restore_temp"
tar xzf "$BACKUP_FILE" -C "$BACKUP_DIR/restore_temp"

# Function to restore a volume
restore_volume() {
    local volume_name=$1
    local backup_file="$BACKUP_DIR/restore_temp/$BACKUP_NAME/${volume_name}.tar.gz"
    
    if [ -f "$backup_file" ]; then
        echo "📦 Restoring volume: $volume_name"
        
        # Create a temporary container to restore the volume
        docker run --rm -v "$volume_name:/data" -v "$(pwd)/$BACKUP_DIR/restore_temp/$BACKUP_NAME:/backup" \
            alpine sh -c "rm -rf /data/* && tar xzf /backup/${volume_name}.tar.gz -C /data"
        
        echo "✅ Restored $volume_name"
    else
        echo "⚠️  Warning: Backup file not found for $volume_name: $backup_file"
    fi
}

# Restore all volumes
echo "🔄 Restoring API data..."
restore_volume "graphrag_api_data"
restore_volume "graphrag_api_logs"
restore_volume "graphrag_api_cache"
restore_volume "graphrag_api_models"
restore_volume "graphrag_api_documents"
restore_volume "graphrag_api_exports"

echo "🔄 Restoring frontend data..."
restore_volume "graphrag_frontend_data"
restore_volume "graphrag_frontend_logs"

echo "🔄 Restoring Neo4j data..."
restore_volume "graphrag_neo4j_data"
restore_volume "graphrag_neo4j_logs"
restore_volume "graphrag_neo4j_import"
restore_volume "graphrag_neo4j_plugins"
restore_volume "graphrag_neo4j_backup"

echo "🔄 Restoring Qdrant data..."
restore_volume "graphrag_qdrant_data"
restore_volume "graphrag_qdrant_logs"
restore_volume "graphrag_qdrant_snapshots"

echo "🔄 Restoring Redis data..."
restore_volume "graphrag_redis_data"
restore_volume "graphrag_redis_logs"

echo "🔄 Restoring NER API data..."
restore_volume "graphrag_ner_cache"
restore_volume "graphrag_ner_models"
restore_volume "graphrag_ner_logs"

echo "🔄 Restoring Relationship API data..."
restore_volume "graphrag_rel_cache"
restore_volume "graphrag_rel_models"
restore_volume "graphrag_rel_logs"

# Clean up temporary files
echo "🧹 Cleaning up temporary files..."
rm -rf "$BACKUP_DIR/restore_temp"

    # Start services
    echo "🚀 Starting GraphRAG services..."
    docker compose up -d

echo "✅ Restore completed successfully!"
echo "📊 Services are starting up..."
echo "🔍 Check service status with: docker-compose ps"
echo "📋 View logs with: docker-compose logs -f" 