# Knowledge Graph Filtering and Limiting

This document describes the new filtering and limiting capabilities for the knowledge graph to make results more manageable for the UI.

## Overview

The knowledge graph can become unwieldy with thousands of entities and relationships. The new filtering system allows you to:

1. **Limit results** - Cap the number of entities and relationships returned
2. **Filter by occurrence** - Only show entities/relationships that appear a minimum number of times
3. **Filter by confidence** - Filter by confidence scores
4. **Filter by type** - Filter by entity types or relationship types
5. **Sort results** - Sort by occurrence, confidence, or name
6. **Domain filtering** - Filter by specific domains

## New Endpoints

### 1. Filtered Knowledge Graph Export

**POST** `/knowledge-graph/filtered`

Get filtered knowledge graph data with comprehensive filtering options.

**Request Body:**
```json
{
  "domain": "general",
  "max_entities": 100,
  "max_relationships": 200,
  "min_occurrence": 1,
  "min_confidence": 0.0,
  "entity_types": ["COMPONENT", "SYSTEM"],
  "relationship_types": ["part of", "connected to"],
  "sort_by": "occurrence",
  "sort_order": "desc"
}
```

**Response:**
```json
{
  "filtered_data": {
    "entities": [...],
    "relationships": [...],
    "total_entities_before_filter": 2444,
    "total_relationships_before_filter": 36533,
    "filters_applied": {...}
  },
  "filters_applied": {...},
  "total_entities_before_filter": 2444,
  "total_relationships_before_filter": 36533,
  "entities_after_filter": 20,
  "relationships_after_filter": 30
}
```

### 2. Top Entities

**GET** `/knowledge-graph/top-entities`

Get top entities by occurrence count.

**Query Parameters:**
- `domain` (optional): Filter by domain
- `limit` (default: 50): Maximum number of entities to return
- `min_occurrence` (default: 1): Minimum occurrence count
- `entity_type` (optional): Filter by entity type

**Example:**
```
GET /knowledge-graph/top-entities?limit=10&min_occurrence=5
```

### 3. Top Relationships

**GET** `/knowledge-graph/top-relationships`

Get top relationships by weight/occurrence count.

**Query Parameters:**
- `domain` (optional): Filter by domain
- `limit` (default: 50): Maximum number of relationships to return
- `min_weight` (default: 1): Minimum weight/occurrence count
- `relationship_type` (optional): Filter by relationship type

**Example:**
```
GET /knowledge-graph/top-relationships?limit=10&min_weight=50
```

### 4. Enhanced Export

**GET** `/knowledge-graph/export`

Enhanced export endpoint with filtering support.

**Query Parameters:**
- `format` (default: "json"): Export format
- `domain` (optional): Filter by domain
- `max_entities` (default: 1000): Maximum entities to export
- `max_relationships` (default: 2000): Maximum relationships to export
- `min_occurrence` (default: 1): Minimum occurrence count

**Example:**
```
GET /knowledge-graph/export?max_entities=50&max_relationships=100&min_occurrence=5
```

## Filtering Options

### Occurrence Threshold
- **Purpose**: Only show entities/relationships that appear frequently enough to be meaningful
- **Usage**: Set `min_occurrence` to filter out rare entities
- **Example**: `min_occurrence=5` shows only entities that appear 5+ times

### Result Limiting
- **Purpose**: Prevent overwhelming the UI with too many results
- **Usage**: Set `max_entities` and `max_relationships` to cap results
- **Example**: `max_entities=50` returns at most 50 entities

### Confidence Filtering
- **Purpose**: Filter by extraction confidence scores
- **Usage**: Set `min_confidence` to show only high-confidence extractions
- **Example**: `min_confidence=0.8` shows only entities with 80%+ confidence

### Type Filtering
- **Purpose**: Focus on specific entity or relationship types
- **Usage**: Set `entity_types` or `relationship_types` arrays
- **Example**: `entity_types=["COMPONENT", "SYSTEM"]` shows only components and systems

### Sorting Options
- **occurrence**: Sort by occurrence count (most frequent first)
- **confidence**: Sort by confidence score (highest first)
- **name**: Sort alphabetically by entity/relationship name
- **sort_order**: "asc" or "desc"

## Use Cases

### 1. UI Dashboard
```json
{
  "max_entities": 20,
  "max_relationships": 30,
  "min_occurrence": 5,
  "entity_types": ["COMPONENT", "SYSTEM"],
  "sort_by": "occurrence",
  "sort_order": "desc"
}
```

### 2. Detailed Analysis
```json
{
  "max_entities": 100,
  "max_relationships": 200,
  "min_occurrence": 2,
  "min_confidence": 0.7,
  "sort_by": "confidence",
  "sort_order": "desc"
}
```

### 3. Domain-Specific View
```json
{
  "domain": "automotive",
  "max_entities": 50,
  "max_relationships": 100,
  "min_occurrence": 3,
  "entity_types": ["COMPONENT"],
  "relationship_types": ["part of", "connected to"]
}
```

## Performance Benefits

1. **Reduced Data Transfer**: Filtering reduces payload size significantly
2. **Faster UI Rendering**: Fewer entities/relationships to process
3. **Better User Experience**: More relevant, focused results
4. **Scalable**: System can handle large knowledge graphs efficiently

## Implementation Details

The filtering is implemented in the `KnowledgeGraphBuilder` class with these new methods:

- `get_filtered_graph_data()`: Comprehensive filtering with all options
- `get_top_entities()`: Get top entities by occurrence
- `get_top_relationships()`: Get top relationships by weight

All filtering is done in-memory using NetworkX graph operations for optimal performance. 