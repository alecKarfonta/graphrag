#!/usr/bin/env python3

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import json
from entity_extractor import Entity, Relationship
from graph_reasoner import GraphReasoner, ReasoningPath, ReasoningResult
from entity_linker import EntityLinker

@dataclass
class QueryExpansion:
    """Represents query expansion results."""
    original_query: str
    expanded_terms: List[str]
    entity_links: List[str]
    relationship_terms: List[str]
    reasoning_paths: List[ReasoningPath]
    confidence: float

@dataclass
class EnhancedSearchResult:
    """Enhanced search result with graph-based reasoning."""
    query: str
    results: List[Dict[str, Any]]
    reasoning_paths: List[ReasoningPath]
    inferred_relationships: List[Relationship]
    entity_clusters: List[List[str]]
    explanation: List[str]
    confidence: float

class EnhancedQueryProcessor:
    """Enhanced query processor with graph-based reasoning capabilities."""
    
    def __init__(self):
        """Initialize the enhanced query processor."""
        self.graph_reasoner = GraphReasoner()
        self.entity_linker = EntityLinker()
        
        # Query patterns for different reasoning types
        self.reasoning_patterns = {
            "relationship_query": [
                r"how (is|are) (.+) (related|connected|linked) to (.+)",
                r"what (is|are) the (relationship|connection) between (.+) and (.+)",
                r"explain (the )?(relationship|connection) between (.+) and (.+)"
            ],
            "multi_hop_query": [
                r"what (connects|links|relates) (.+) to (.+)",
                r"find (the )?(path|route) from (.+) to (.+)",
                r"how (does|do) (.+) (connect|link|relate) to (.+)"
            ],
            "entity_exploration": [
                r"what (is|are) (.+) (related|connected|linked) to",
                r"find (all )?(entities|components) (related|connected|linked) to (.+)",
                r"explore (.+) (relationships|connections)"
            ]
        }
    
    def process_query(self, query: str, entities: List[Entity], relationships: List[Relationship]) -> EnhancedSearchResult:
        """Process a query with graph-based reasoning."""
        # Build the knowledge graph
        self.graph_reasoner.build_graph(entities, relationships)
        
        # Analyze query type
        query_type = self._classify_query(query)
        
        # Extract entities from query
        query_entities = self._extract_entities_from_query(query, entities)
        
        # Perform query expansion
        expansion = self._expand_query(query, query_entities, relationships)
        
        # Execute search based on query type
        if query_type == "relationship_query":
            result = self._handle_relationship_query(query, query_entities)
        elif query_type == "multi_hop_query":
            result = self._handle_multi_hop_query(query, query_entities)
        elif query_type == "entity_exploration":
            result = self._handle_entity_exploration_query(query, query_entities)
        else:
            result = self._handle_general_query(query, expansion)
        
        return result
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query."""
        query_lower = query.lower()
        
        for query_type, patterns in self.reasoning_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return query_type
        
        return "general_query"
    
    def _extract_entities_from_query(self, query: str, available_entities: List[Entity]) -> List[Entity]:
        """Extract entities mentioned in the query."""
        query_lower = query.lower()
        found_entities = []
        
        for entity in available_entities:
            entity_name_lower = entity.name.lower()
            
            # Check for exact match
            if entity_name_lower in query_lower:
                found_entities.append(entity)
            # Check for partial match
            elif any(word in entity_name_lower for word in entity_name_lower.split()):
                if any(word in query_lower for word in entity_name_lower.split()):
                    found_entities.append(entity)
        
        return found_entities
    
    def _expand_query(self, query: str, query_entities: List[Entity], relationships: List[Relationship]) -> QueryExpansion:
        """Expand query using graph-based reasoning."""
        expanded_terms = []
        entity_links = []
        relationship_terms = []
        reasoning_paths = []
        
        # Find related entities for each query entity
        for entity in query_entities:
            related = self.graph_reasoner.find_related_entities(entity.name, max_hops=2)
            
            for hop_level, related_list in related.items():
                for related_entity, confidence in related_list:
                    if confidence > 0.5:  # Only include high-confidence relationships
                        expanded_terms.append(related_entity)
                        entity_links.append(f"{entity.name} -> {related_entity}")
        
        # Extract relationship terms from the query
        relationship_keywords = ["related", "connected", "linked", "part of", "contains", "works for", "located in"]
        for keyword in relationship_keywords:
            if keyword in query.lower():
                relationship_terms.append(keyword)
        
        # Find reasoning paths if we have multiple entities
        if len(query_entities) >= 2:
            for i in range(len(query_entities)):
                for j in range(i + 1, len(query_entities)):
                    paths = self.graph_reasoner.find_paths(
                        query_entities[i].name, 
                        query_entities[j].name, 
                        max_hops=3
                    )
                    reasoning_paths.extend(paths)
        
        return QueryExpansion(
            original_query=query,
            expanded_terms=expanded_terms,
            entity_links=entity_links,
            relationship_terms=relationship_terms,
            reasoning_paths=reasoning_paths,
            confidence=0.8
        )
    
    def _handle_relationship_query(self, query: str, query_entities: List[Entity]) -> EnhancedSearchResult:
        """Handle queries asking about relationships between entities."""
        if len(query_entities) < 2:
            return self._create_empty_result(query, "Need at least two entities to analyze relationships")
        
        # Get the first two entities for relationship analysis
        entity1, entity2 = query_entities[0], query_entities[1]
        
        # Explain the relationship
        reasoning_result = self.graph_reasoner.explain_relationship(entity1.name, entity2.name)
        
        # Find related entities
        related_entities = self.graph_reasoner.find_related_entities(entity1.name, max_hops=2)
        
        # Create results
        results = []
        for hop_level, entities in related_entities.items():
            for entity_name, confidence in entities:
                if entity_name != entity1.name:
                    results.append({
                        "entity": entity_name,
                        "relationship": hop_level,
                        "confidence": confidence,
                        "source_entity": entity1.name
                    })
        
        return EnhancedSearchResult(
            query=query,
            results=results,
            reasoning_paths=reasoning_result.paths,
            inferred_relationships=reasoning_result.inferred_relationships,
            entity_clusters=self.graph_reasoner.find_entity_clusters(),
            explanation=reasoning_result.reasoning_steps,
            confidence=reasoning_result.confidence
        )
    
    def _handle_multi_hop_query(self, query: str, query_entities: List[Entity]) -> EnhancedSearchResult:
        """Handle multi-hop reasoning queries."""
        if len(query_entities) < 2:
            return self._create_empty_result(query, "Need at least two entities for multi-hop reasoning")
        
        entity1, entity2 = query_entities[0], query_entities[1]
        
        # Find all paths between entities
        paths = self.graph_reasoner.find_paths(entity1.name, entity2.name, max_hops=4)
        
        # Infer relationships from paths
        inferred_rels = self.graph_reasoner.infer_relationships(entity1.name, entity2.name, max_hops=4)
        
        # Create results showing the paths
        results = []
        for path in paths[:5]:  # Top 5 paths
            results.append({
                "path": path.path,
                "relationships": path.relationships,
                "confidence": path.confidence,
                "length": path.path_length
            })
        
        explanation = [
            f"Found {len(paths)} paths between {entity1.name} and {entity2.name}",
            f"Path lengths range from 1 to {max([p.path_length for p in paths]) if paths else 0} hops",
            f"Top path confidence: {max([p.confidence for p in paths]) if paths else 0:.2f}"
        ]
        
        return EnhancedSearchResult(
            query=query,
            results=results,
            reasoning_paths=paths,
            inferred_relationships=inferred_rels,
            entity_clusters=self.graph_reasoner.find_entity_clusters(),
            explanation=explanation,
            confidence=max([p.confidence for p in paths]) if paths else 0.0
        )
    
    def _handle_entity_exploration_query(self, query: str, query_entities: List[Entity]) -> EnhancedSearchResult:
        """Handle queries exploring entities and their relationships."""
        if not query_entities:
            return self._create_empty_result(query, "No entities found in query")
        
        entity = query_entities[0]
        
        # Find related entities
        related_entities = self.graph_reasoner.find_related_entities(entity.name, max_hops=3)
        
        # Get entity centrality
        centrality = self.graph_reasoner.get_entity_centrality()
        
        # Create results
        results = []
        for hop_level, entities in related_entities.items():
            for entity_name, confidence in entities:
                centrality_info = centrality.get(entity_name, {})
                results.append({
                    "entity": entity_name,
                    "relationship_level": hop_level,
                    "confidence": confidence,
                    "centrality": centrality_info.get("overall", 0),
                    "source_entity": entity.name
                })
        
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        explanation = [
            f"Found {len(results)} entities related to {entity.name}",
            f"Relationship levels: {list(related_entities.keys())}",
            f"Average confidence: {sum(r['confidence'] for r in results) / len(results) if results else 0:.2f}"
        ]
        
        return EnhancedSearchResult(
            query=query,
            results=results,
            reasoning_paths=[],
            inferred_relationships=[],
            entity_clusters=self.graph_reasoner.find_entity_clusters(),
            explanation=explanation,
            confidence=0.8
        )
    
    def _handle_general_query(self, query: str, expansion: QueryExpansion) -> EnhancedSearchResult:
        """Handle general queries with graph-based expansion."""
        # Use expanded terms to enhance search
        enhanced_query = query + " " + " ".join(expansion.expanded_terms[:5])
        
        # Find relevant entities based on expansion
        results = []
        for entity_link in expansion.entity_links[:10]:
            source, target = entity_link.split(" -> ")
            results.append({
                "entity": target,
                "relationship": "related to",
                "confidence": 0.7,
                "source_entity": source
            })
        
        explanation = [
            f"Expanded query with {len(expansion.expanded_terms)} terms",
            f"Found {len(expansion.entity_links)} entity relationships",
            f"Query expansion confidence: {expansion.confidence:.2f}"
        ]
        
        return EnhancedSearchResult(
            query=query,
            results=results,
            reasoning_paths=expansion.reasoning_paths,
            inferred_relationships=[],
            entity_clusters=self.graph_reasoner.find_entity_clusters(),
            explanation=explanation,
            confidence=expansion.confidence
        )
    
    def _create_empty_result(self, query: str, message: str) -> EnhancedSearchResult:
        """Create an empty search result."""
        return EnhancedSearchResult(
            query=query,
            results=[],
            reasoning_paths=[],
            inferred_relationships=[],
            entity_clusters=[],
            explanation=[message],
            confidence=0.0
        )
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get statistics about query processing."""
        graph_stats = self.graph_reasoner.get_graph_statistics()
        entity_stats = self.entity_linker.get_entity_statistics()
        
        return {
            "graph_statistics": graph_stats,
            "entity_statistics": entity_stats,
            "total_entities": len(self.graph_reasoner.entity_cache),
            "total_relationships": self.graph_reasoner.graph.number_of_edges()
        } 