#!/bin/bash

# GraphRAG Backup Script
# This script creates backups of all persistent data volumes

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="graphrag_backup_$TIMESTAMP"

echo "🚀 Starting GraphRAG backup..."
echo "📁 Backup directory: $BACKUP_DIR"
echo "📦 Backup name: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Function to backup a volume
backup_volume() {
    local volume_name=$1
    local backup_path=$2
    
    echo "📦 Backing up volume: $volume_name"
    
    # Create a temporary container to access the volume
    docker run --rm -v "$volume_name:/data" -v "$(pwd)/$BACKUP_DIR/$BACKUP_NAME:/backup" \
        alpine tar czf "/backup/${volume_name}.tar.gz" -C /data .
    
    echo "✅ Backed up $volume_name to $BACKUP_DIR/$BACKUP_NAME/${volume_name}.tar.gz"
}

# Backup all volumes
echo "🔄 Backing up API data..."
backup_volume "graphrag_api_data" "api_data"
backup_volume "graphrag_api_logs" "api_logs"
backup_volume "graphrag_api_cache" "api_cache"
backup_volume "graphrag_api_models" "api_models"
backup_volume "graphrag_api_documents" "api_documents"
backup_volume "graphrag_api_exports" "api_exports"

echo "🔄 Backing up frontend data..."
backup_volume "graphrag_frontend_data" "frontend_data"
backup_volume "graphrag_frontend_logs" "frontend_logs"

echo "🔄 Backing up Neo4j data..."
backup_volume "graphrag_neo4j_data" "neo4j_data"
backup_volume "graphrag_neo4j_logs" "neo4j_logs"
backup_volume "graphrag_neo4j_import" "neo4j_import"
backup_volume "graphrag_neo4j_plugins" "neo4j_plugins"
backup_volume "graphrag_neo4j_backup" "neo4j_backup"

echo "🔄 Backing up Qdrant data..."
backup_volume "graphrag_qdrant_data" "qdrant_data"
backup_volume "graphrag_qdrant_logs" "qdrant_logs"
backup_volume "graphrag_qdrant_snapshots" "qdrant_snapshots"

echo "🔄 Backing up Redis data..."
backup_volume "graphrag_redis_data" "redis_data"
backup_volume "graphrag_redis_logs" "redis_logs"

echo "🔄 Backing up NER API data..."
backup_volume "graphrag_ner_cache" "ner_cache"
backup_volume "graphrag_ner_models" "ner_models"
backup_volume "graphrag_ner_logs" "ner_logs"

echo "🔄 Backing up Relationship API data..."
backup_volume "graphrag_rel_cache" "rel_cache"
backup_volume "graphrag_rel_models" "rel_models"
backup_volume "graphrag_rel_logs" "rel_logs"

# Create backup metadata
cat > "$BACKUP_DIR/$BACKUP_NAME/backup_info.txt" << EOF
GraphRAG Backup Information
==========================
Backup Date: $(date)
Backup Name: $BACKUP_NAME
Docker Compose Version: $(docker compose version --short)

Backed up volumes:
- API data, logs, cache, models, documents, exports
- Frontend data and logs
- Neo4j data, logs, import, plugins, backup
- Qdrant data, logs, snapshots
- Redis data and logs
- NER API cache, models, logs
- Relationship API cache, models, logs

To restore this backup, run:
./scripts/restore.sh $BACKUP_NAME
EOF

# Create compressed archive
echo "📦 Creating compressed archive..."
cd "$BACKUP_DIR"
tar czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

echo "✅ Backup completed successfully!"
echo "📁 Backup location: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "📊 Backup size: $(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)" 