# GraphRAG Persistent Storage

This document describes the persistent storage setup for GraphRAG, ensuring that all data survives container restarts and deployments.

## Overview

GraphRAG uses Docker volumes to provide persistent storage for all critical data:

- **Knowledge Graph Data** (Neo4j)
- **Vector Embeddings** (Qdrant)
- **Cached Models** (NER, Relationship APIs)
- **Application Data** (API logs, documents, exports)
- **Frontend Data** (User preferences, cached data)

## Persistent Volumes

### API Service Volumes
- `api_data`: Application data and configurations
- `api_logs`: Application logs
- `api_cache`: Cached data and temporary files
- `api_models`: Downloaded ML models
- `api_documents`: Uploaded and processed documents
- `api_exports`: Exported data and reports

### Frontend Volumes
- `frontend_data`: User data and preferences
- `frontend_logs`: Frontend application logs

### Database Volumes
- `neo4j_data`: Neo4j database files
- `neo4j_logs`: Neo4j transaction logs
- `neo4j_import`: Import directory for data loading
- `neo4j_plugins`: Neo4j plugins and extensions
- `neo4j_backup`: Neo4j backup files

### Vector Database Volumes
- `qdrant_data`: Qdrant vector database storage
- `qdrant_logs`: Qdrant application logs
- `qdrant_snapshots`: Qdrant snapshots for backup

### Cache Volumes
- `redis_data`: Redis database files
- `redis_logs`: Redis application logs

### ML Service Volumes
- `ner_cache`: NER API model cache
- `ner_models`: NER API downloaded models
- `ner_logs`: NER API application logs
- `rel_cache`: Relationship API model cache
- `rel_models`: Relationship API downloaded models
- `rel_logs`: Relationship API application logs

## Data Management

### Backup and Restore

#### Creating a Backup
```bash
./scripts/backup.sh
```

This creates a timestamped backup of all persistent volumes in the `./backups/` directory.

#### Restoring from Backup
```bash
./scripts/restore.sh <backup_name>
```

Example:
```bash
./scripts/restore.sh graphrag_backup_20241201_143022
```

### Data Management Commands

#### List Volumes and Sizes
```bash
./scripts/manage_data.sh list-volumes
```

#### List Available Backups
```bash
./scripts/manage_data.sh list-backups
```

#### Storage Information
```bash
./scripts/manage_data.sh storage-info
```

#### Health Check
```bash
./scripts/manage_data.sh health-check
```

#### Cleanup Unused Resources
```bash
./scripts/manage_data.sh cleanup
```

## Migration and Deployment

### Moving to a New Server

1. **Create a backup on the old server:**
   ```bash
   ./scripts/backup.sh
   ```

2. **Transfer the backup file:**
   ```bash
   scp ./backups/graphrag_backup_*.tar.gz user@new-server:/path/to/graphrag/
   ```

3. **Restore on the new server:**
   ```bash
   ./scripts/restore.sh graphrag_backup_YYYYMMDD_HHMMSS
   ```

### Upgrading GraphRAG

1. **Create a backup before upgrade:**
   ```bash
   ./scripts/backup.sh
   ```

2. **Update the code and rebuild:**
   ```bash
   git pull
   docker-compose up -d --build
   ```

3. **Verify data integrity:**
   ```bash
   ./scripts/manage_data.sh health-check
   ```

## Monitoring and Maintenance

### Regular Maintenance Tasks

1. **Weekly Health Check:**
   ```bash
   ./scripts/manage_data.sh health-check
   ```

2. **Monthly Backup:**
   ```bash
   ./scripts/backup.sh
   ```

3. **Quarterly Cleanup:**
   ```bash
   ./scripts/manage_data.sh cleanup
   ```

### Storage Monitoring

Monitor storage usage with:
```bash
./scripts/manage_data.sh storage-info
```

### Volume Inspection

To inspect a specific volume:
```bash
docker run --rm -v graphrag_neo4j_data:/data alpine ls -la /data
```

## Troubleshooting

### Common Issues

#### Volume Not Found
If a volume is missing, check if it exists:
```bash
docker volume ls | grep graphrag
```

#### Permission Issues
If you encounter permission issues, ensure the volumes are owned by the correct user:
```bash
docker run --rm -v graphrag_api_data:/data alpine chown -R 1000:1000 /data
```

#### Storage Full
If storage is full, clean up unused resources:
```bash
./scripts/manage_data.sh cleanup
docker system prune -a
```

### Recovery Procedures

#### Complete System Recovery
1. Stop all services: `docker-compose down`
2. Restore from backup: `./scripts/restore.sh <backup_name>`
3. Start services: `docker-compose up -d`
4. Verify health: `./scripts/manage_data.sh health-check`

#### Individual Service Recovery
If a specific service fails:
1. Check logs: `docker-compose logs <service_name>`
2. Restart service: `docker-compose restart <service_name>`
3. Verify volume health: `./scripts/manage_data.sh health-check`

## Security Considerations

### Volume Security
- All volumes use local drivers for better security
- Volumes are isolated from the host system
- Regular backups ensure data recovery capability

### Backup Security
- Backups are stored in the `./backups/` directory
- Backup files are compressed and timestamped
- Consider encrypting backup files for sensitive data

### Access Control
- Volumes are accessible only to the containers that need them
- No direct host access to volume data
- Use Docker secrets for sensitive configuration

## Performance Optimization

### Volume Performance
- Use SSD storage for better I/O performance
- Monitor volume sizes and clean up regularly
- Consider using volume drivers optimized for your storage backend

### Backup Performance
- Backups are compressed to save space
- Incremental backups can be implemented for large datasets
- Schedule backups during low-usage periods

## Best Practices

1. **Regular Backups:** Create backups before major changes
2. **Monitor Storage:** Keep track of volume sizes and growth
3. **Health Checks:** Run health checks regularly
4. **Documentation:** Document any custom volume configurations
5. **Testing:** Test backup and restore procedures regularly

## Configuration

### Volume Configuration
All volumes are configured in `docker-compose.yml` with local drivers for maximum compatibility and security.

### Backup Configuration
Backup scripts are located in `./scripts/` and can be customized for specific requirements.

### Monitoring Configuration
Health check and monitoring scripts provide comprehensive system status information. 