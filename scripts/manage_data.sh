#!/bin/bash

# GraphRAG Data Management Script
# This script helps manage persistent data volumes

set -e

show_help() {
    echo "GraphRAG Data Management Script"
    echo "==============================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  list-volumes    List all persistent volumes and their sizes"
    echo "  list-backups    List available backups"
    echo "  cleanup         Clean up unused volumes and containers"
    echo "  storage-info    Show detailed storage information"
    echo "  health-check    Check health of all services and volumes"
    echo "  help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 list-volumes"
    echo "  $0 storage-info"
    echo "  $0 health-check"
}

list_volumes() {
    echo "📦 GraphRAG Persistent Volumes"
    echo "=============================="
    echo ""
    
    # List all volumes with sizes
    docker volume ls --format "table {{.Name}}\t{{.Driver}}" | grep graphrag || echo "No GraphRAG volumes found"
    
    echo ""
    echo "📊 Volume Sizes:"
    echo "================"
    
    for volume in $(docker volume ls -q | grep graphrag); do
        size=$(docker run --rm -v "$volume:/data" alpine du -sh /data 2>/dev/null | cut -f1 || echo "Unknown")
        echo "$volume: $size"
    done
}

list_backups() {
    echo "📦 Available Backups"
    echo "===================="
    echo ""
    
    BACKUP_DIR="./backups"
    if [ -d "$BACKUP_DIR" ]; then
        if [ "$(ls -A "$BACKUP_DIR"/*.tar.gz 2>/dev/null)" ]; then
            for backup in "$BACKUP_DIR"/*.tar.gz; do
                if [ -f "$backup" ]; then
                    filename=$(basename "$backup")
                    size=$(du -h "$backup" | cut -f1)
                    date=$(stat -c %y "$backup" | cut -d' ' -f1)
                    echo "$filename ($size) - $date"
                fi
            done
        else
            echo "No backups found in $BACKUP_DIR"
        fi
    else
        echo "Backup directory $BACKUP_DIR does not exist"
    fi
}

cleanup() {
    echo "🧹 Cleaning up unused Docker resources..."
    echo ""
    
    echo "📦 Removing unused volumes..."
    docker volume prune -f
    
    echo "🐳 Removing unused containers..."
    docker container prune -f
    
    echo "🖼️  Removing unused images..."
    docker image prune -f
    
    echo "🌐 Removing unused networks..."
    docker network prune -f
    
    echo "✅ Cleanup completed!"
}

storage_info() {
    echo "📊 GraphRAG Storage Information"
    echo "==============================="
    echo ""
    
    # System storage
    echo "💾 System Storage:"
    df -h | grep -E "(Filesystem|/dev/)"
    echo ""
    
    # Docker storage
    echo "🐳 Docker Storage:"
    docker system df
    echo ""
    
    # Volume storage
    echo "📦 Volume Storage:"
    total_size=0
    for volume in $(docker volume ls -q | grep graphrag); do
        size=$(docker run --rm -v "$volume:/data" alpine du -sh /data 2>/dev/null | cut -f1 || echo "0")
        echo "$volume: $size"
        # Convert size to bytes for total calculation (simplified)
        if [[ $size =~ ^[0-9]+[KMG] ]]; then
            total_size=$((total_size + 1))
        fi
    done
    echo ""
    
    # Backup storage
    BACKUP_DIR="./backups"
    if [ -d "$BACKUP_DIR" ]; then
        backup_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "0")
        echo "📦 Backup Storage: $backup_size"
    fi
}

health_check() {
    echo "🏥 GraphRAG Health Check"
    echo "========================"
    echo ""
    
    # Check if services are running
    echo "🔍 Service Status:"
    docker compose ps
    echo ""
    
    # Check volume health
    echo "📦 Volume Health:"
    for volume in $(docker volume ls -q | grep graphrag); do
        if docker run --rm -v "$volume:/data" alpine test -d /data 2>/dev/null; then
            echo "✅ $volume: Healthy"
        else
            echo "❌ $volume: Unhealthy"
        fi
    done
    echo ""
    
    # Check API health
    echo "🌐 API Health:"
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Main API: Healthy"
    else
        echo "❌ Main API: Unhealthy"
    fi
    
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ NER API: Healthy"
    else
        echo "❌ NER API: Unhealthy"
    fi
    
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo "✅ Relationship API: Healthy"
    else
        echo "❌ Relationship API: Unhealthy"
    fi
    echo ""
    
    # Check database connections
    echo "🗄️  Database Health:"
    if docker compose exec -T neo4j cypher-shell -u neo4j -p password "RETURN 1" > /dev/null 2>&1; then
        echo "✅ Neo4j: Connected"
    else
        echo "❌ Neo4j: Connection failed"
    fi
    
    if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
        echo "✅ Qdrant: Connected"
    else
        echo "❌ Qdrant: Connection failed"
    fi
    
    if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis: Connected"
    else
        echo "❌ Redis: Connection failed"
    fi
}

# Main script logic
case "${1:-help}" in
    "list-volumes")
        list_volumes
        ;;
    "list-backups")
        list_backups
        ;;
    "cleanup")
        cleanup
        ;;
    "storage-info")
        storage_info
        ;;
    "health-check")
        health_check
        ;;
    "help"|*)
        show_help
        ;;
esac 