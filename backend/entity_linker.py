#!/usr/bin/env python3

import re
import string
from typing import List, Dict, Any, Tuple, Optional
from difflib import SequenceMatcher
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from entity_extractor import Entity

@dataclass
class EntityLink:
    """Represents a link between similar entities."""
    source_entity: Entity
    target_entity: Entity
    similarity_score: float
    link_type: str  # "exact", "fuzzy", "semantic", "disambiguation"
    confidence: float
    metadata: Dict[str, Any]

class EntityLinker:
    """Links similar entities across documents and handles disambiguation."""
    
    def __init__(self):
        """Initialize the entity linker."""
        self.entity_clusters = defaultdict(list)  # cluster_id -> [entities]
        self.entity_to_cluster = {}  # entity_id -> cluster_id
        self.next_cluster_id = 0
        
        # Load spaCy for better text processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("⚠️ spaCy model not found. Installing...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize TF-IDF vectorizer for semantic similarity
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        self.entity_vectors = {}
        self.vectorizer_fitted = False
    
    def link_entities(self, entities: List[Entity], existing_entities: List[Entity] = None) -> List[EntityLink]:
        """Link new entities with existing ones and create clusters."""
        if existing_entities is None:
            existing_entities = []
        
        links = []
        
        # Process new entities
        for entity in entities:
            # Find best match among existing entities
            best_match = self._find_best_match(entity, existing_entities)
            
            if best_match:
                # Create link
                link = EntityLink(
                    source_entity=entity,
                    target_entity=best_match,
                    similarity_score=best_match[1],
                    link_type=best_match[2],
                    confidence=best_match[1],
                    metadata={"method": "entity_linking"}
                )
                links.append(link)
                
                # Add to cluster
                self._add_to_cluster(entity, best_match[0])
            else:
                # Create new cluster
                self._create_new_cluster(entity)
        
        return links
    
    def _find_best_match(self, entity: Entity, existing_entities: List[Entity]) -> Optional[Tuple[Entity, float, str]]:
        """Find the best matching entity among existing ones."""
        best_match = None
        best_score = 0.0
        best_type = ""
        
        for existing in existing_entities:
            # Exact match
            if self._exact_match(entity, existing):
                return (existing, 1.0, "exact")
            
            # Fuzzy match
            fuzzy_score = self._fuzzy_similarity(entity.name, existing.name)
            if fuzzy_score > 0.8 and fuzzy_score > best_score:
                best_match = existing
                best_score = fuzzy_score
                best_type = "fuzzy"
            
            # Semantic similarity
            semantic_score = self._semantic_similarity(entity, existing)
            if semantic_score > 0.7 and semantic_score > best_score:
                best_match = existing
                best_score = semantic_score
                best_type = "semantic"
        
        if best_score > 0.6:
            return (best_match, best_score, best_type)
        
        return None
    
    def _exact_match(self, entity1: Entity, entity2: Entity) -> bool:
        """Check for exact match (case-insensitive)."""
        return (entity1.name.lower().strip() == entity2.name.lower().strip() and
                entity1.entity_type == entity2.entity_type)
    
    def _fuzzy_similarity(self, name1: str, name2: str) -> float:
        """Calculate fuzzy string similarity."""
        # Normalize names
        name1 = self._normalize_entity_name(name1)
        name2 = self._normalize_entity_name(name2)
        
        # Use sequence matcher
        similarity = SequenceMatcher(None, name1, name2).ratio()
        
        # Additional checks for abbreviations and variations
        if self._is_abbreviation(name1, name2) or self._is_abbreviation(name2, name1):
            similarity = max(similarity, 0.8)
        
        return similarity
    
    def _normalize_entity_name(self, name: str) -> str:
        """Normalize entity name for comparison."""
        # Remove punctuation and extra spaces
        name = re.sub(r'[^\w\s]', ' ', name)
        name = ' '.join(name.split())
        return name.lower()
    
    def _is_abbreviation(self, short: str, long: str) -> bool:
        """Check if one name is an abbreviation of the other."""
        short = short.replace('.', '').upper()
        long_words = long.upper().split()
        
        if len(short) <= 2:
            return False
        
        # Check if short is initials of long
        if len(short) == len(long_words):
            return all(short[i] == long_words[i][0] for i in range(len(short)))
        
        return False
    
    def _semantic_similarity(self, entity1: Entity, entity2: Entity) -> float:
        """Calculate semantic similarity between entities."""
        # Prepare text for vectorization
        text1 = f"{entity1.name} {entity1.entity_type}"
        text2 = f"{entity2.name} {entity2.entity_type}"
        
        # Add context if available
        if entity1.description:
            text1 += f" {entity1.description}"
        if entity2.description:
            text2 += f" {entity2.description}"
        
        # Vectorize
        if not self.vectorizer_fitted:
            self.vectorizer.fit([text1, text2])
            self.vectorizer_fitted = True
        
        vectors = self.vectorizer.transform([text1, text2])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        return similarity
    
    def _add_to_cluster(self, entity: Entity, cluster_entity: Entity):
        """Add entity to existing cluster."""
        cluster_id = self.entity_to_cluster.get(cluster_entity.name, None)
        if cluster_id is None:
            cluster_id = self._create_new_cluster(cluster_entity)
        
        self.entity_clusters[cluster_id].append(entity)
        self.entity_to_cluster[entity.name] = cluster_id
    
    def _create_new_cluster(self, entity: Entity) -> int:
        """Create a new cluster for an entity."""
        cluster_id = self.next_cluster_id
        self.next_cluster_id += 1
        
        self.entity_clusters[cluster_id].append(entity)
        self.entity_to_cluster[entity.name] = cluster_id
        
        return cluster_id
    
    def disambiguate_entity(self, entity: Entity, context: str) -> Entity:
        """Disambiguate entity based on context."""
        # Find all entities with similar names
        candidates = []
        for cluster_id, cluster_entities in self.entity_clusters.items():
            for cluster_entity in cluster_entities:
                if self._fuzzy_similarity(entity.name, cluster_entity.name) > 0.6:
                    candidates.append(cluster_entity)
        
        if not candidates:
            return entity
        
        # Score candidates based on context similarity
        best_candidate = entity
        best_score = 0.0
        
        for candidate in candidates:
            # Create context vectors
            context_text = f"{candidate.name} {candidate.entity_type}"
            if candidate.description:
                context_text += f" {candidate.description}"
            
            # Compare with input context
            similarity = self._context_similarity(context_text, context)
            
            if similarity > best_score:
                best_score = similarity
                best_candidate = candidate
        
        return best_candidate
    
    def _context_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text contexts."""
        # Use TF-IDF for context similarity
        if not self.vectorizer_fitted:
            self.vectorizer.fit([text1, text2])
            self.vectorizer_fitted = True
        
        vectors = self.vectorizer.transform([text1, text2])
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        return similarity
    
    def get_entity_clusters(self) -> Dict[int, List[Entity]]:
        """Get all entity clusters."""
        return dict(self.entity_clusters)
    
    def get_entity_links(self) -> List[EntityLink]:
        """Get all entity links."""
        links = []
        for cluster_id, entities in self.entity_clusters.items():
            if len(entities) > 1:
                # Create links between all entities in cluster
                for i in range(len(entities)):
                    for j in range(i + 1, len(entities)):
                        link = EntityLink(
                            source_entity=entities[i],
                            target_entity=entities[j],
                            similarity_score=0.8,  # Default for cluster members
                            link_type="cluster",
                            confidence=0.8,
                            metadata={"cluster_id": cluster_id}
                        )
                        links.append(link)
        
        return links
    
    def merge_clusters(self, cluster_id1: int, cluster_id2: int):
        """Merge two entity clusters."""
        if cluster_id1 not in self.entity_clusters or cluster_id2 not in self.entity_clusters:
            return
        
        # Move all entities from cluster2 to cluster1
        entities_to_move = self.entity_clusters[cluster_id2]
        self.entity_clusters[cluster_id1].extend(entities_to_move)
        
        # Update entity_to_cluster mapping
        for entity in entities_to_move:
            self.entity_to_cluster[entity.name] = cluster_id1
        
        # Remove cluster2
        del self.entity_clusters[cluster_id2]
    
    def get_entity_statistics(self) -> Dict[str, Any]:
        """Get statistics about entity linking."""
        total_entities = sum(len(entities) for entities in self.entity_clusters.values())
        total_clusters = len(self.entity_clusters)
        
        return {
            "total_entities": total_entities,
            "total_clusters": total_clusters,
            "average_cluster_size": total_entities / total_clusters if total_clusters > 0 else 0,
            "largest_cluster_size": max(len(entities) for entities in self.entity_clusters.values()) if self.entity_clusters else 0
        } 