from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
import json
import re
import os
from ner_client import get_ner_client, is_ner_available
from rel_extractor import get_relationship_extractor

@dataclass
class Entity:
    """Represents an extracted entity."""
    name: str
    entity_type: str
    description: str | None = None
    confidence: float = 1.0
    source_chunk: str | None = None
    metadata: Dict[str, Any] | None = None

@dataclass
class Relationship:
    """Represents a relationship between entities."""
    source: str
    target: str
    relation_type: str
    context: str | None = None
    confidence: float = 1.0
    metadata: Dict[str, Any] | None = None

@dataclass
class ExtractionResult:
    """Result of entity and relationship extraction."""
    entities: List[Entity]
    relationships: List[Relationship]
    claims: List[str]
    source_chunk: str

class EntityExtractor:
    """LLM-based entity and relationship extractor using Claude."""
    
    def __init__(self, model_name: str = "claude-3-sonnet-20240229", api_key: str | None = None, disable_llm_fallback: bool = True):
        """Initialize the entity extractor with Claude."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.disable_llm_fallback = disable_llm_fallback or os.getenv("DISABLE_LLM_FALLBACK", "false").lower() == "true"
        
        # Always initialize LLM for response generation, regardless of disable_llm_fallback
        if self.api_key:
            try:
                self.llm = ChatAnthropic(
                    model=model_name,
                    temperature=0.1,
                    max_tokens=2048,
                    anthropic_api_key=self.api_key
                )
                print("✅ LLM initialized for response generation")
            except Exception as e:
                print(f"⚠️ Could not initialize LLM: {e}")
                self.llm = None
        else:
            print("⚠️ No ANTHROPIC_API_KEY found. LLM features will be disabled.")
            self.llm = None
        
        # Check if we should disable LLM fallback for entity/relationship extraction
        if self.disable_llm_fallback:
            print("ℹ️ LLM fallback disabled for entity/relationship extraction (will use local models only)")
        else:
            print("ℹ️ LLM fallback enabled for entity/relationship extraction")
        
        # Define entity types for different domains
        self.entity_types = {
            "general": ["PERSON", "ORGANIZATION", "LOCATION", "CONCEPT", "PROCESS"],
            "technical": ["COMPONENT", "SPECIFICATION", "PROCEDURE", "SYSTEM", "INTERFACE"],
            "automotive": ["COMPONENT", "SPECIFICATION", "PROCEDURE", "MAINTENANCE_ITEM", "SYMPTOM", "SOLUTION"],
            "medical": ["SYMPTOM", "DIAGNOSIS", "TREATMENT", "MEDICATION", "PROCEDURE"],
            "legal": ["LAW", "REGULATION", "CASE", "PRECEDENT", "JURISDICTION"]
        }
        
        # Define relationship types
        self.relationship_types = {
            "general": ["RELATES_TO", "PART_OF", "CONTAINS", "CAUSES", "REQUIRES"],
            "technical": ["CONNECTS_TO", "DEPENDS_ON", "IMPLEMENTS", "CONFIGURES", "MONITORS"],
            "automotive": ["PART_OF", "CONNECTS_TO", "REQUIRES", "CAUSES", "FIXES", "SCHEDULED_AT"],
            "medical": ["TREATS", "CAUSES", "SYMPTOM_OF", "PRESCRIBED_FOR", "INTERACTS_WITH"],
            "legal": ["AMENDS", "CITES", "OVERRULES", "APPLIES_TO", "DEFINES"]
        }
    
    def extract_entities_and_relations(self, text_chunk: str, domain: str = "general") -> ExtractionResult:
        """Extract entities and relationships from text using local NER API first, then GLiNER, then fall back to Claude."""
        # First, try to use the local NER API
        if is_ner_available():
            try:
                print(f"🔍 Using local NER API for entity extraction...")
                ner_client = get_ner_client()
                ner_result = ner_client.extract_entities(text_chunk)
                
                if ner_result and "entities" in ner_result:
                    print(f"🔍 NER API returned {len(ner_result['entities'])} entities")
                    # Convert NER API results to our Entity format
                    entities = []
                    for ner_entity in ner_result["entities"]:
                        # Map NER entity types to our domain types
                        entity_type = self._map_ner_entity_type(ner_entity["entity"], domain)
                        entity = Entity(
                            name=ner_entity["word"],
                            entity_type=entity_type,
                            description=f"Extracted by local NER model (confidence: {ner_entity['score']:.3f})",
                            confidence=ner_entity["score"],
                            source_chunk=text_chunk,
                            metadata={
                                "domain": domain,
                                "ner_source": "local_model",
                                "original_ner_type": ner_entity["entity"]
                            }
                        )
                        entities.append(entity)
                    if entities:
                        print(f"✅ Local NER found {len(entities)} entities")
                        # Try GLiNER for relationship extraction
                        rel_extractor = get_relationship_extractor()
                        if rel_extractor.is_available():
                            try:
                                print(f"🔗 Using GLiNER for relationship extraction...")
                                # Use a focused set of relationships that are more likely to be found in real text
                                default_relations = [
                                    # Business/Organizational relationships
                                    {"relation": "works for", "pairs_filter": [("person", "organisation")]},
                                    {"relation": "founded", "pairs_filter": [("person", "organisation")]},
                                    {"relation": "located in", "pairs_filter": [("organisation", "location"), ("person", "location")]},
                                    {"relation": "acquired", "pairs_filter": [("organisation", "organisation")]},
                                    {"relation": "subsidiary of", "pairs_filter": [("organisation", "organisation")]},
                                    {"relation": "produces", "pairs_filter": [("organisation", "product")]},
                                    {"relation": "part of", "pairs_filter": [("organisation", "organisation")]},
                                    
                                    # Technical/Component relationships (simplified)
                                    {"relation": "part of", "pairs_filter": [("component", "component"), ("system", "component")]},
                                    {"relation": "connects to", "pairs_filter": [("component", "component")]},
                                    {"relation": "contains", "pairs_filter": [("component", "component"), ("system", "component")]},
                                    {"relation": "controls", "pairs_filter": [("component", "component")]},
                                    {"relation": "supplies", "pairs_filter": [("component", "component")]},
                                    {"relation": "replaces", "pairs_filter": [("component", "component")]},
                                    {"relation": "maintains", "pairs_filter": [("procedure", "component"), ("maintenance", "component")]},
                                    {"relation": "requires", "pairs_filter": [("component", "component"), ("procedure", "component")]},
                                    {"relation": "causes", "pairs_filter": [("component", "symptom"), ("condition", "symptom")]},
                                    {"relation": "fixes", "pairs_filter": [("solution", "symptom"), ("procedure", "symptom")]},
                                    
                                    # Temporal relationships
                                    {"relation": "scheduled for", "pairs_filter": [("maintenance", "time"), ("procedure", "time")]},
                                    {"relation": "created on", "pairs_filter": [("organisation", "date"), ("product", "date")]},
                                    
                                    # Specification relationships
                                    {"relation": "specifies", "pairs_filter": [("specification", "component"), ("requirement", "component")]},
                                    {"relation": "applies to", "pairs_filter": [("specification", "component"), ("requirement", "component")]},
                                    
                                    # General relationships (less restrictive filters)
                                    {"relation": "related to", "pairs_filter": [("component", "component"), ("system", "component"), ("organisation", "organisation"), ("person", "organisation")]},
                                    {"relation": "associated with", "pairs_filter": [("component", "component"), ("system", "component"), ("organisation", "organisation"), ("person", "organisation")]},
                                    {"relation": "depends on", "pairs_filter": [("component", "component"), ("system", "component"), ("procedure", "component")]},
                                    {"relation": "affects", "pairs_filter": [("component", "component"), ("condition", "symptom"), ("procedure", "component")]},
                                    {"relation": "influences", "pairs_filter": [("component", "component"), ("condition", "symptom"), ("procedure", "component")]},
                                    {"relation": "supports", "pairs_filter": [("component", "component"), ("system", "component")]},
                                    {"relation": "enables", "pairs_filter": [("component", "component"), ("system", "component")]},
                                    {"relation": "prevents", "pairs_filter": [("component", "component"), ("safety", "component")]},
                                    {"relation": "protects", "pairs_filter": [("component", "component"), ("safety", "component")]},
                                    {"relation": "monitors", "pairs_filter": [("component", "component"), ("system", "component")]},
                                    {"relation": "regulates", "pairs_filter": [("component", "component"), ("system", "component")]},
                                    {"relation": "operates", "pairs_filter": [("component", "component"), ("system", "component")]},
                                    {"relation": "manages", "pairs_filter": [("component", "component"), ("system", "component"), ("person", "organisation")]},
                                    {"relation": "directs", "pairs_filter": [("person", "organisation"), ("organisation", "organisation")]},
                                    {"relation": "leads", "pairs_filter": [("person", "organisation"), ("organisation", "organisation")]},
                                    {"relation": "owns", "pairs_filter": [("person", "organisation"), ("organisation", "organisation")]},
                                    {"relation": "invests in", "pairs_filter": [("person", "organisation"), ("organisation", "organisation")]},
                                    {"relation": "collaborates with", "pairs_filter": [("organisation", "organisation"), ("person", "organisation")]},
                                    {"relation": "competes with", "pairs_filter": [("organisation", "organisation")]},
                                    {"relation": "partners with", "pairs_filter": [("organisation", "organisation")]},
                                ]
                                entity_labels = list({e.entity_type.lower() for e in entities})
                                gliner_result = rel_extractor.extract_relations(
                                    text=text_chunk,
                                    relations=default_relations,
                                    entity_labels=entity_labels,
                                    threshold=0.5
                                )
                                relationships = []
                                for rel in gliner_result.get("relations", []):
                                    relationships.append(Relationship(
                                        source=rel.get("source") or rel.get("text", ""),
                                        target=rel.get("target", ""),
                                        relation_type=rel.get("label", rel.get("relation", "")),
                                        context=rel.get("context", None),
                                        confidence=rel.get("score", 1.0),
                                        metadata={"extraction_method": "gliner"}
                                    ))
                                
                                # Apply validation and filtering
                                entities = self.validate_entities(entities)
                                relationships = self.validate_relationships(relationships, entities)
                                
                                print(f"✅ After validation: {len(entities)} entities, {len(relationships)} relationships")
                                
                                return ExtractionResult(
                                    entities=entities,
                                    relationships=relationships,
                                    claims=[],
                                    source_chunk=text_chunk
                                )
                            except Exception as e:
                                print(f"⚠️ GLiNER relationship extraction failed: {e}, falling back to LLM")
                        # Use LLM only for relationship extraction if GLiNER is unavailable or fails
                        relationships, claims = self._extract_relationships_with_llm(text_chunk, entities, domain)
                        
                        # Apply validation and filtering
                        entities = self.validate_entities(entities)
                        relationships = self.validate_relationships(relationships, entities)
                        
                        print(f"✅ After validation: {len(entities)} entities, {len(relationships)} relationships")
                        
                        return ExtractionResult(
                            entities=entities,
                            relationships=relationships,
                            claims=claims,
                            source_chunk=text_chunk
                        )
                    else:
                        print(f"⚠️ Local NER returned no valid entities, trying GLiNER for entity extraction...")
                        # Try GLiNER for entity extraction when local NER fails
                        rel_extractor = get_relationship_extractor()
                        if rel_extractor.is_available():
                            try:
                                print(f"🔍 Using GLiNER for entity extraction...")
                                # Use GLiNER to extract entities
                                gliner_entities = rel_extractor.extract_entities(
                                    text=text_chunk,
                                    labels=["person", "organisation", "location", "date", "product", "component", "system", "procedure", "symptom", "solution", "maintenance", "specification", "requirement", "safety", "time"],
                                    threshold=0.5
                                )
                                
                                if gliner_entities.get("entities"):
                                    print(f"✅ GLiNER found {len(gliner_entities['entities'])} entities")
                                    entities = []
                                    for gliner_entity in gliner_entities["entities"]:
                                        entity = Entity(
                                            name=gliner_entity["text"],
                                            entity_type=gliner_entity["label"].upper(),
                                            description=f"Extracted by GLiNER model (confidence: {gliner_entity['score']:.3f})",
                                            confidence=gliner_entity["score"],
                                            source_chunk=text_chunk,
                                            metadata={
                                                "domain": domain,
                                                "ner_source": "gliner_model",
                                                "original_ner_type": gliner_entity["label"]
                                            }
                                        )
                                        entities.append(entity)
                                    
                                    # Now extract relationships with GLiNER
                                    print(f"🔗 Using GLiNER for relationship extraction...")
                                    default_relations = [
                                        # Business/Organizational relationships
                                        {"relation": "works for", "pairs_filter": [("person", "organisation")]},
                                        {"relation": "founded", "pairs_filter": [("person", "organisation")]},
                                        {"relation": "located in", "pairs_filter": [("organisation", "location"), ("person", "location")]},
                                        {"relation": "acquired", "pairs_filter": [("organisation", "organisation")]},
                                        {"relation": "subsidiary of", "pairs_filter": [("organisation", "organisation")]},
                                        {"relation": "produces", "pairs_filter": [("organisation", "product")]},
                                        {"relation": "part of", "pairs_filter": [("organisation", "organisation")]},
                                        
                                        # Technical/Component relationships (simplified)
                                        {"relation": "part of", "pairs_filter": [("component", "component"), ("system", "component")]},
                                        {"relation": "connects to", "pairs_filter": [("component", "component")]},
                                        {"relation": "contains", "pairs_filter": [("component", "component"), ("system", "component")]},
                                        {"relation": "controls", "pairs_filter": [("component", "component")]},
                                        {"relation": "supplies", "pairs_filter": [("component", "component")]},
                                        {"relation": "replaces", "pairs_filter": [("component", "component")]},
                                        {"relation": "maintains", "pairs_filter": [("procedure", "component"), ("maintenance", "component")]},
                                        {"relation": "requires", "pairs_filter": [("component", "component"), ("procedure", "component")]},
                                        {"relation": "causes", "pairs_filter": [("component", "symptom"), ("condition", "symptom")]},
                                        {"relation": "fixes", "pairs_filter": [("solution", "symptom"), ("procedure", "symptom")]},
                                        
                                        # Temporal relationships
                                        {"relation": "scheduled for", "pairs_filter": [("maintenance", "time"), ("procedure", "time")]},
                                        {"relation": "created on", "pairs_filter": [("organisation", "date"), ("product", "date")]},
                                        
                                        # Specification relationships
                                        {"relation": "specifies", "pairs_filter": [("specification", "component"), ("requirement", "component")]},
                                        {"relation": "applies to", "pairs_filter": [("specification", "component"), ("requirement", "component")]},
                                    ]
                                    entity_labels = list({e.entity_type.lower() for e in entities})
                                    gliner_result = rel_extractor.extract_relations(
                                        text=text_chunk,
                                        relations=default_relations,
                                        entity_labels=entity_labels,
                                        threshold=0.5
                                    )
                                    relationships = []
                                    for rel in gliner_result.get("relations", []):
                                        relationships.append(Relationship(
                                            source=rel.get("source") or rel.get("text", ""),
                                            target=rel.get("target", ""),
                                            relation_type=rel.get("label", rel.get("relation", "")),
                                            context=rel.get("context", None),
                                            confidence=rel.get("score", 1.0),
                                            metadata={"extraction_method": "gliner"}
                                        ))
                                    
                                    # Apply validation and filtering
                                    entities = self.validate_entities(entities)
                                    relationships = self.validate_relationships(relationships, entities)
                                    
                                    print(f"✅ After validation: {len(entities)} entities, {len(relationships)} relationships")
                                    
                                    return ExtractionResult(
                                        entities=entities,
                                        relationships=relationships,
                                        claims=[],
                                        source_chunk=text_chunk
                                    )
                                else:
                                    if self.disable_llm_fallback:
                                        print(f"⚠️ GLiNER also returned no entities, LLM fallback disabled - skipping extraction")
                                        return ExtractionResult(
                                            entities=[],
                                            relationships=[],
                                            claims=[],
                                            source_chunk=text_chunk
                                        )
                                    else:
                                        print(f"⚠️ GLiNER also returned no entities, falling back to LLM")
                            except Exception as e:
                                if self.disable_llm_fallback:
                                    print(f"⚠️ GLiNER entity extraction failed: {e}, LLM fallback disabled - skipping extraction")
                                    return ExtractionResult(
                                        entities=[],
                                        relationships=[],
                                        claims=[],
                                        source_chunk=text_chunk
                                    )
                                else:
                                    print(f"⚠️ GLiNER entity extraction failed: {e}, falling back to LLM")
                        else:
                            if self.disable_llm_fallback:
                                print(f"⚠️ GLiNER not available, LLM fallback disabled - skipping extraction")
                                return ExtractionResult(
                                    entities=[],
                                    relationships=[],
                                    claims=[],
                                    source_chunk=text_chunk
                                )
                            else:
                                print(f"⚠️ GLiNER not available, falling back to LLM")
                else:
                    print(f"⚠️ Local NER API returned no entities or invalid response, trying GLiNER...")
                    # Try GLiNER for entity extraction when local NER fails
                    rel_extractor = get_relationship_extractor()
                    if rel_extractor.is_available():
                        try:
                            print(f"🔍 Using GLiNER for entity extraction...")
                            # Use GLiNER to extract entities
                            gliner_entities = rel_extractor.extract_entities(
                                text=text_chunk,
                                labels=["person", "organisation", "location", "date", "product", "component", "system", "procedure", "symptom", "solution", "maintenance", "specification", "requirement", "safety", "time"],
                                threshold=0.5
                            )
                            
                            if gliner_entities.get("entities"):
                                print(f"✅ GLiNER found {len(gliner_entities['entities'])} entities")
                                entities = []
                                for gliner_entity in gliner_entities["entities"]:
                                    entity = Entity(
                                        name=gliner_entity["text"],
                                        entity_type=gliner_entity["label"].upper(),
                                        description=f"Extracted by GLiNER model (confidence: {gliner_entity['score']:.3f})",
                                        confidence=gliner_entity["score"],
                                        source_chunk=text_chunk,
                                        metadata={
                                            "domain": domain,
                                            "ner_source": "gliner_model",
                                            "original_ner_type": gliner_entity["label"]
                                        }
                                    )
                                    entities.append(entity)
                                
                                # Now extract relationships with GLiNER
                                print(f"🔗 Using GLiNER for relationship extraction...")
                                default_relations = [
                                    # Business/Organizational relationships
                                    {"relation": "works for", "pairs_filter": [("person", "organisation")]},
                                    {"relation": "founded", "pairs_filter": [("person", "organisation")]},
                                    {"relation": "located in", "pairs_filter": [("organisation", "location"), ("person", "location")]},
                                    {"relation": "acquired", "pairs_filter": [("organisation", "organisation")]},
                                    {"relation": "subsidiary of", "pairs_filter": [("organisation", "organisation")]},
                                    {"relation": "produces", "pairs_filter": [("organisation", "product")]},
                                    {"relation": "part of", "pairs_filter": [("organisation", "organisation")]},
                                    
                                    # Technical/Component relationships (simplified)
                                    {"relation": "part of", "pairs_filter": [("component", "component"), ("system", "component")]},
                                    {"relation": "connects to", "pairs_filter": [("component", "component")]},
                                    {"relation": "contains", "pairs_filter": [("component", "component"), ("system", "component")]},
                                    {"relation": "controls", "pairs_filter": [("component", "component")]},
                                    {"relation": "supplies", "pairs_filter": [("component", "component")]},
                                    {"relation": "replaces", "pairs_filter": [("component", "component")]},
                                    {"relation": "maintains", "pairs_filter": [("procedure", "component"), ("maintenance", "component")]},
                                    {"relation": "requires", "pairs_filter": [("component", "component"), ("procedure", "component")]},
                                    {"relation": "causes", "pairs_filter": [("component", "symptom"), ("condition", "symptom")]},
                                    {"relation": "fixes", "pairs_filter": [("solution", "symptom"), ("procedure", "symptom")]},
                                    
                                    # Temporal relationships
                                    {"relation": "scheduled for", "pairs_filter": [("maintenance", "time"), ("procedure", "time")]},
                                    {"relation": "created on", "pairs_filter": [("organisation", "date"), ("product", "date")]},
                                    
                                    # Specification relationships
                                    {"relation": "specifies", "pairs_filter": [("specification", "component"), ("requirement", "component")]},
                                    {"relation": "applies to", "pairs_filter": [("specification", "component"), ("requirement", "component")]},
                                ]
                                entity_labels = list({e.entity_type.lower() for e in entities})
                                gliner_result = rel_extractor.extract_relations(
                                    text=text_chunk,
                                    relations=default_relations,
                                    entity_labels=entity_labels,
                                    threshold=0.5
                                )
                                relationships = []
                                for rel in gliner_result.get("relations", []):
                                    relationships.append(Relationship(
                                        source=rel.get("source") or rel.get("text", ""),
                                        target=rel.get("target", ""),
                                        relation_type=rel.get("label", rel.get("relation", "")),
                                        context=rel.get("context", None),
                                        confidence=rel.get("score", 1.0),
                                        metadata={"extraction_method": "gliner"}
                                    ))
                                
                                # Apply validation and filtering
                                entities = self.validate_entities(entities)
                                relationships = self.validate_relationships(relationships, entities)
                                
                                print(f"✅ After validation: {len(entities)} entities, {len(relationships)} relationships")
                                
                                return ExtractionResult(
                                    entities=entities,
                                    relationships=relationships,
                                    claims=[],
                                    source_chunk=text_chunk
                                )
                            else:
                                if self.disable_llm_fallback:
                                    print(f"⚠️ GLiNER also returned no entities, LLM fallback disabled - skipping extraction")
                                    return ExtractionResult(
                                        entities=[],
                                        relationships=[],
                                        claims=[],
                                        source_chunk=text_chunk
                                    )
                                else:
                                    print(f"⚠️ GLiNER also returned no entities, falling back to LLM")
                        except Exception as e:
                            if self.disable_llm_fallback:
                                print(f"⚠️ GLiNER entity extraction failed: {e}, LLM fallback disabled - skipping extraction")
                                return ExtractionResult(
                                    entities=[],
                                    relationships=[],
                                    claims=[],
                                    source_chunk=text_chunk
                                )
                            else:
                                print(f"⚠️ GLiNER entity extraction failed: {e}, falling back to LLM")
                    else:
                        if self.disable_llm_fallback:
                            print(f"⚠️ GLiNER not available, LLM fallback disabled - skipping extraction")
                            return ExtractionResult(
                                entities=[],
                                relationships=[],
                                claims=[],
                                source_chunk=text_chunk
                            )
                        else:
                            print(f"⚠️ GLiNER not available, falling back to LLM")
            except Exception as e:
                print(f"⚠️ Local NER API failed: {e}, trying GLiNER...")
                # Try GLiNER for entity extraction when local NER fails
                rel_extractor = get_relationship_extractor()
                if rel_extractor.is_available():
                    try:
                        print(f"🔍 Using GLiNER for entity extraction...")
                        # Use GLiNER to extract entities
                        gliner_entities = rel_extractor.extract_entities(
                            text=text_chunk,
                            labels=["person", "organisation", "location", "date", "product", "component", "system", "procedure", "symptom", "solution", "maintenance", "specification", "requirement", "safety", "time"],
                            threshold=0.5
                        )
                        
                        if gliner_entities.get("entities"):
                            print(f"✅ GLiNER found {len(gliner_entities['entities'])} entities")
                            entities = []
                            for gliner_entity in gliner_entities["entities"]:
                                entity = Entity(
                                    name=gliner_entity["text"],
                                    entity_type=gliner_entity["label"].upper(),
                                    description=f"Extracted by GLiNER model (confidence: {gliner_entity['score']:.3f})",
                                    confidence=gliner_entity["score"],
                                    source_chunk=text_chunk,
                                    metadata={
                                        "domain": domain,
                                        "ner_source": "gliner_model",
                                        "original_ner_type": gliner_entity["label"]
                                    }
                                )
                                entities.append(entity)
                            
                            # Now extract relationships with GLiNER
                            print(f"🔗 Using GLiNER for relationship extraction...")
                            default_relations = [
                                # Business/Organizational relationships
                                {"relation": "works for", "pairs_filter": [("person", "organisation")]},
                                {"relation": "founded", "pairs_filter": [("person", "organisation")]},
                                {"relation": "located in", "pairs_filter": [("organisation", "location"), ("person", "location")]},
                                {"relation": "acquired", "pairs_filter": [("organisation", "organisation")]},
                                {"relation": "subsidiary of", "pairs_filter": [("organisation", "organisation")]},
                                {"relation": "produces", "pairs_filter": [("organisation", "product")]},
                                {"relation": "part of", "pairs_filter": [("organisation", "organisation")]},
                                
                                # Technical/Component relationships (simplified)
                                {"relation": "part of", "pairs_filter": [("component", "component"), ("system", "component")]},
                                {"relation": "connects to", "pairs_filter": [("component", "component")]},
                                {"relation": "contains", "pairs_filter": [("component", "component"), ("system", "component")]},
                                {"relation": "controls", "pairs_filter": [("component", "component")]},
                                {"relation": "supplies", "pairs_filter": [("component", "component")]},
                                {"relation": "replaces", "pairs_filter": [("component", "component")]},
                                {"relation": "maintains", "pairs_filter": [("procedure", "component"), ("maintenance", "component")]},
                                {"relation": "requires", "pairs_filter": [("component", "component"), ("procedure", "component")]},
                                {"relation": "causes", "pairs_filter": [("component", "symptom"), ("condition", "symptom")]},
                                {"relation": "fixes", "pairs_filter": [("solution", "symptom"), ("procedure", "symptom")]},
                                
                                # Temporal relationships
                                {"relation": "scheduled for", "pairs_filter": [("maintenance", "time"), ("procedure", "time")]},
                                {"relation": "created on", "pairs_filter": [("organisation", "date"), ("product", "date")]},
                                
                                # Specification relationships
                                {"relation": "specifies", "pairs_filter": [("specification", "component"), ("requirement", "component")]},
                                {"relation": "applies to", "pairs_filter": [("specification", "component"), ("requirement", "component")]},
                            ]
                            entity_labels = list({e.entity_type.lower() for e in entities})
                            gliner_result = rel_extractor.extract_relations(
                                text=text_chunk,
                                relations=default_relations,
                                entity_labels=entity_labels,
                                threshold=0.5
                            )
                            relationships = []
                            for rel in gliner_result.get("relations", []):
                                relationships.append(Relationship(
                                    source=rel.get("source") or rel.get("text", ""),
                                    target=rel.get("target", ""),
                                    relation_type=rel.get("label", rel.get("relation", "")),
                                    context=rel.get("context", None),
                                    confidence=rel.get("score", 1.0),
                                    metadata={"extraction_method": "gliner"}
                                ))
                            
                            # Apply validation and filtering
                            entities = self.validate_entities(entities)
                            relationships = self.validate_relationships(relationships, entities)
                            
                            print(f"✅ After validation: {len(entities)} entities, {len(relationships)} relationships")
                            
                            return ExtractionResult(
                                entities=entities,
                                relationships=relationships,
                                claims=[],
                                source_chunk=text_chunk
                            )
                        else:
                            if self.disable_llm_fallback:
                                print(f"⚠️ GLiNER also returned no entities, LLM fallback disabled - skipping extraction")
                                return ExtractionResult(
                                    entities=[],
                                    relationships=[],
                                    claims=[],
                                    source_chunk=text_chunk
                                )
                            else:
                                print(f"⚠️ GLiNER also returned no entities, falling back to LLM")
                    except Exception as e:
                        if self.disable_llm_fallback:
                            print(f"⚠️ GLiNER entity extraction failed: {e}, LLM fallback disabled - skipping extraction")
                            return ExtractionResult(
                                entities=[],
                                relationships=[],
                                claims=[],
                                source_chunk=text_chunk
                            )
                        else:
                            print(f"⚠️ GLiNER entity extraction failed: {e}, falling back to LLM")
                else:
                    if self.disable_llm_fallback:
                        print(f"⚠️ GLiNER not available, LLM fallback disabled - skipping extraction")
                        return ExtractionResult(
                            entities=[],
                            relationships=[],
                            claims=[],
                            source_chunk=text_chunk
                        )
                    else:
                        print(f"⚠️ GLiNER not available, falling back to LLM")
        
        # Fall back to LLM-based extraction (only if not disabled)
        if self.disable_llm_fallback:
            print(f"⚠️ LLM fallback disabled - skipping extraction")
            return ExtractionResult(
                entities=[],
                relationships=[],
                claims=[],
                source_chunk=text_chunk
            )
        else:
            print(f"🔍 Using LLM-based entity extraction...")
            return self._extract_with_llm(text_chunk, domain)
    
    def _map_ner_entity_type(self, ner_type: str, domain: str) -> str:
        """Map NER entity types to domain-specific types."""
        # Remove I- prefix from NER types (e.g., I-PER -> PER)
        clean_type = ner_type.replace("I-", "").replace("B-", "")
        
        # Map to domain-specific types
        type_mapping = {
            "PER": "PERSON",
            "ORG": "ORGANIZATION", 
            "LOC": "LOCATION",
            "MISC": "CONCEPT"
        }
        
        return type_mapping.get(clean_type, "CONCEPT")
    
    def _extract_relationships_with_llm(self, text_chunk: str, entities: List[Entity], domain: str) -> tuple[List[Relationship], List[str]]:
        """Extract relationships using LLM given the entities."""
        # Check if LLM fallback is disabled
        if self.disable_llm_fallback:
            print(f"⚠️ LLM fallback disabled for relationship extraction - skipping")
            return [], []
        
        if not self.llm:
            return [], []
        
        # Create a focused prompt for relationship extraction
        entity_names = [e.name for e in entities]
        entity_text = ", ".join(entity_names)
        
        prompt = ChatPromptTemplate.from_template("""
        Given these entities: {entities}
        
        Extract relationships between these entities from the text below.
        
        Return JSON with this exact format:
        {{
            "relationships": [
                {{
                    "source": "Source Entity",
                    "target": "Target Entity", 
                    "relation": "RELATES_TO|PART_OF|CONTAINS|CAUSES|REQUIRES",
                    "context": "Brief context",
                    "confidence": 0.9
                }}
            ],
            "claims": ["Important fact 1", "Important fact 2"]
        }}
        
        Text: {text}
        """)
        
        try:
            response = self.llm.invoke(prompt.format(entities=entity_text, text=text_chunk))
            result_data = self._parse_claude_response(response.content)
            
            relationships = []
            for rel_data in result_data.get("relationships", []):
                relationship = Relationship(
                    source=rel_data["source"],
                    target=rel_data["target"],
                    relation_type=rel_data["relation"],
                    context=rel_data.get("context"),
                    confidence=rel_data.get("confidence", 1.0),
                    metadata={"domain": domain, "extraction_method": "llm"}
                )
                relationships.append(relationship)
            
            claims = result_data.get("claims", [])
            return relationships, claims
            
        except Exception as e:
            print(f"Error in LLM relationship extraction: {e}")
            return [], []
    
    def _extract_with_llm(self, text_chunk: str, domain: str) -> ExtractionResult:
        """Extract entities and relationships using LLM (fallback method)."""
        
        # Check if LLM fallback is disabled
        if self.disable_llm_fallback:
            print(f"⚠️ LLM fallback disabled - skipping extraction")
            return ExtractionResult(
                entities=[],
                relationships=[],
                claims=[],
                source_chunk=text_chunk
            )
        
        # Get entity and relationship types for the domain
        entity_types = self.entity_types.get(domain, self.entity_types["general"])
        relationship_types = self.relationship_types.get(domain, self.relationship_types["general"])
        
        prompt = ChatPromptTemplate.from_template("""
        Extract entities and relationships from the text below.
        
        Return JSON with this exact format:
        {{
            "entities": [
                {{
                    "name": "Entity Name",
                    "type": "PERSON|ORGANIZATION|LOCATION|CONCEPT|PRODUCT",
                    "description": "Brief description",
                    "confidence": 0.9
                }}
            ],
            "relationships": [
                {{
                    "source": "Source Entity",
                    "target": "Target Entity", 
                    "relation": "MANUFACTURES|CONTAINS|CONNECTS_TO|PART_OF|HAS",
                    "context": "Brief context",
                    "confidence": 0.9
                }}
            ],
            "claims": ["Important fact 1", "Important fact 2"]
        }}
        
        IMPORTANT: Always include relationships between entities you find.
        
        Text: {text}
        """)
        
        try:
            # Generate response from Claude
            response = self.llm.invoke(prompt.format(text=text_chunk))
            
            # Use robust parsing
            result_data = self._parse_claude_response(response.content)
            
            # Convert to structured objects
            entities = []
            for entity_data in result_data.get("entities", []):
                entity = Entity(
                    name=entity_data["name"],
                    entity_type=entity_data["type"],
                    description=entity_data.get("description"),
                    confidence=entity_data.get("confidence", 1.0),
                    source_chunk=text_chunk,
                    metadata={"domain": domain, "extraction_method": "llm"}
                )
                entities.append(entity)
            
            relationships = []
            for rel_data in result_data.get("relationships", []):
                relationship = Relationship(
                    source=rel_data["source"],
                    target=rel_data["target"],
                    relation_type=rel_data["relation"],
                    context=rel_data.get("context"),
                    confidence=rel_data.get("confidence", 1.0),
                    metadata={"domain": domain, "extraction_method": "llm"}
                )
                relationships.append(relationship)
            
            claims = result_data.get("claims", [])
            
            # Apply validation and filtering
            entities = self.validate_entities(entities)
            relationships = self.validate_relationships(relationships, entities)
            
            print(f"✅ After validation: {len(entities)} entities, {len(relationships)} relationships")
            
            return ExtractionResult(
                entities=entities,
                relationships=relationships,
                claims=claims,
                source_chunk=text_chunk
            )
            
        except Exception as e:
            print(f"Error in entity extraction: {e}")
            return ExtractionResult(entities=[], relationships=[], claims=[], source_chunk=text_chunk)
    
    def extract_from_chunks(self, chunks: List[str], domain: str = "general") -> List[ExtractionResult]:
        """Extract entities and relationships from multiple text chunks."""
        results = []
        
        for chunk in chunks:
            result = self.extract_entities_and_relations(chunk, domain)
            results.append(result)
        
        return results
    
    def extract_with_context(self, text_chunk: str, context: str, domain: str = "general") -> ExtractionResult:
        """Extract entities with additional context."""
        enhanced_text = f"Context: {context}\n\nText to analyze: {text_chunk}"
        return self.extract_entities_and_relations(enhanced_text, domain)
    
    def validate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Validate and clean extracted entities with proper deduplication."""
        validated_entities = []
        seen_entities = set()  # Track normalized entity names
        
        for entity in entities:
            # Basic validation
            if not entity.name or len(entity.name.strip()) < 2:
                continue
            
            # Clean entity name
            entity.name = entity.name.strip()
            
            # Normalize for deduplication (lowercase, remove extra spaces)
            normalized_name = " ".join(entity.name.lower().split())
            
            # Skip if we've seen this entity before (case-insensitive)
            if normalized_name in seen_entities:
                continue
            
            # Additional quality checks
            if self._is_low_quality_entity(entity):
                continue
            
            seen_entities.add(normalized_name)
            validated_entities.append(entity)
        
        return validated_entities
    
    def _is_low_quality_entity(self, entity: Entity) -> bool:
        """Check if entity is low quality and should be filtered out."""
        name = entity.name.lower()
        
        # Filter out common noise
        noise_patterns = [
            r'^\d+$',  # Just numbers
            r'^[a-z]$',  # Single letter
            r'^[^\w\s]+$',  # Just punctuation
            r'^(the|a|an|and|or|but|in|on|at|to|for|of|with|by|from|up|down|out|off|over|under|above|below|before|after|during|while|since|until|unless|if|then|else|when|where|why|how|what|which|who|whom|whose|that|this|these|those|it|its|they|them|their|we|us|our|you|your|he|him|his|she|her|hers|i|me|my|mine)$',  # Common words
        ]
        
        for pattern in noise_patterns:
            if re.match(pattern, name):
                return True
        
        # Filter out very short entities (unless they're abbreviations)
        if len(name) < 2 and not name.isupper():
            return True
        
        # Filter out entities that are mostly punctuation
        if len(re.sub(r'[^\w\s]', '', name)) < len(name) * 0.5:
            return True
        
        return False
    
    def validate_relationships(self, relationships: List[Relationship], entities: List[Entity]) -> List[Relationship]:
        """Validate relationships against known entities with quality filtering."""
        entity_names = {entity.name.lower() for entity in entities}
        validated_relationships = []
        seen_relationships = set()  # Track to avoid duplicates
        
        for relationship in relationships:
            # Check if both source and target entities exist (case-insensitive)
            source_exists = any(entity.name.lower() == relationship.source.lower() for entity in entities)
            target_exists = any(entity.name.lower() == relationship.target.lower() for entity in entities)
            
            if not (source_exists and target_exists):
                continue
            
            # Skip self-relationships
            if relationship.source.lower() == relationship.target.lower():
                continue
            
            # Quality checks for relationships
            if self._is_low_quality_relationship(relationship):
                continue
            
            # Create normalized key for deduplication
            rel_key = (relationship.source.lower(), relationship.target.lower(), relationship.relation_type.lower())
            if rel_key in seen_relationships:
                continue
            
            seen_relationships.add(rel_key)
            validated_relationships.append(relationship)
        
        return validated_relationships
    
    def _is_low_quality_relationship(self, relationship: Relationship) -> bool:
        """Check if relationship is low quality and should be filtered out."""
        rel_type = relationship.relation_type.lower()
        source = relationship.source.lower()
        target = relationship.target.lower()
        
        # Filter out generic/meaningless relationships
        generic_relations = [
            'related to', 'associated with', 'connected to', 'linked to',
            'part of', 'contains', 'includes', 'has', 'is', 'are', 'was', 'were'
        ]
        
        if rel_type in generic_relations:
            return True
        
        # Filter out relationships with very short entities
        if len(source) < 2 or len(target) < 2:
            return True
        
        # Filter out relationships where entities are too similar
        if source == target or source in target or target in source:
            return True
        
        # Filter out relationships with common words as entities
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        if source in common_words or target in common_words:
            return True
        
        return False
    
    def _parse_claude_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse Claude's response using multiple robust parsing strategies."""
        
        # Strategy 1: Try standard JSON parsing first
        try:
            # Look for JSON block in code fence
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try direct JSON parsing
            return json.loads(raw_response)
            
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Strategy 2: Extract JSON-like content between braces
        try:
            # Find the main JSON structure
            start = raw_response.find('{')
            if start != -1:
                # Find matching closing brace
                brace_count = 0
                end = start
                for i, char in enumerate(raw_response[start:], start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break
                
                if end > start:
                    json_str = raw_response[start:end]
                    return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Strategy 3: Robust field extraction using regex patterns
        print("[DEBUG] Attempting robust field extraction for entities...")
        
        # Extract entities array
        entities = self._extract_entities_array(raw_response)
        
        # Extract relationships array
        relationships = self._extract_relationships_array(raw_response)
        
        # Extract claims array
        claims = self._extract_claims_array(raw_response)
        
        return {
            "entities": entities,
            "relationships": relationships,
            "claims": claims
        }
    
    def _extract_entities_array(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from malformed JSON response."""
        entities = []
        
        # Look for entities section
        entities_match = re.search(r'"entities":\s*\[(.*?)\]', text, re.DOTALL)
        if not entities_match:
            return entities
        
        entities_text = entities_match.group(1)
        
        # Split by entity objects (look for opening braces)
        entity_blocks = re.findall(r'\{[^}]*\}', entities_text)
        
        for block in entity_blocks:
            entity = {}
            
            # Extract name
            name_match = re.search(r'"name":\s*"([^"]*)"', block)
            if name_match:
                entity["name"] = name_match.group(1)
            
            # Extract type
            type_match = re.search(r'"type":\s*"([^"]*)"', block)
            if type_match:
                entity["type"] = type_match.group(1)
            
            # Extract description
            desc_match = re.search(r'"description":\s*"([^"]*)"', block)
            if desc_match:
                entity["description"] = desc_match.group(1)
            
            # Extract confidence
            conf_match = re.search(r'"confidence":\s*([0-9.]+)', block)
            if conf_match:
                entity["confidence"] = float(conf_match.group(1))
            else:
                entity["confidence"] = 0.8
            
            if entity.get("name") and entity.get("type"):
                entities.append(entity)
        
        # Fallback: extract entity names from text patterns
        if not entities:
            # Look for common entity patterns in the text
            entity_patterns = [
                r'entity[^:]*:\s*"([^"]+)"',
                r'name[^:]*:\s*"([^"]+)"',
                r'"([A-Z][a-zA-Z\s]+)".*(?:PERSON|ORGANIZATION|LOCATION|CONCEPT)',
            ]
            
            for pattern in entity_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match.strip()) > 1:
                        entities.append({
                            "name": match.strip(),
                            "type": "CONCEPT",
                            "description": "Extracted from malformed response",
                            "confidence": 0.6
                        })
        
        return entities
    
    def _extract_relationships_array(self, text: str) -> List[Dict[str, Any]]:
        """Extract relationships from malformed JSON response."""
        relationships = []
        
        # Look for relationships section
        rel_match = re.search(r'"relationships":\s*\[(.*?)\]', text, re.DOTALL)
        if not rel_match:
            print("[DEBUG] No relationships section found in response")
            # Try fallback relationship extraction
            return self._extract_relationships_fallback(text)
        
        rel_text = rel_match.group(1)
        print(f"[DEBUG] Found relationships section: {rel_text[:100]}...")
        
        # Split by relationship objects
        rel_blocks = re.findall(r'\{[^}]*\}', rel_text)
        print(f"[DEBUG] Found {len(rel_blocks)} relationship blocks")
        
        for block in rel_blocks:
            relationship = {}
            
            # Extract source
            source_match = re.search(r'"source":\s*"([^"]*)"', block)
            if source_match:
                relationship["source"] = source_match.group(1)
            
            # Extract target
            target_match = re.search(r'"target":\s*"([^"]*)"', block)
            if target_match:
                relationship["target"] = target_match.group(1)
            
            # Extract relation
            rel_match = re.search(r'"relation":\s*"([^"]*)"', block)
            if rel_match:
                relationship["relation"] = rel_match.group(1)
            
            # Extract context
            context_match = re.search(r'"context":\s*"([^"]*)"', block)
            if context_match:
                relationship["context"] = context_match.group(1)
            
            # Extract confidence
            conf_match = re.search(r'"confidence":\s*([0-9.]+)', block)
            if conf_match:
                relationship["confidence"] = float(conf_match.group(1))
            else:
                relationship["confidence"] = 0.8
            
            if relationship.get("source") and relationship.get("target") and relationship.get("relation"):
                relationships.append(relationship)
                print(f"[DEBUG] Added relationship: {relationship['source']} -> {relationship['relation']} -> {relationship['target']}")
        
        if not relationships:
            print("[DEBUG] No valid relationships found, trying fallback")
            return self._extract_relationships_fallback(text)
        
        return relationships
    
    def _extract_relationships_fallback(self, text: str) -> List[Dict[str, Any]]:
        """Fallback relationship extraction using pattern matching."""
        relationships = []
        
        # Look for common relationship patterns in the text
        relationship_patterns = [
            # Pattern: "Entity1 relates to Entity2"
            r'"([^"]+)"\s+(?:relates to|connects to|is related to)\s+"([^"]+)"',
            # Pattern: "Entity1 is a Entity2"
            r'"([^"]+)"\s+is\s+(?:a|an)\s+"([^"]+)"',
            # Pattern: "Entity1 has Entity2"
            r'"([^"]+)"\s+has\s+"([^"]+)"',
            # Pattern: "Entity1 contains Entity2"
            r'"([^"]+)"\s+contains\s+"([^"]+)"',
            # Pattern: "Entity1 works for Entity2"
            r'"([^"]+)"\s+works for\s+"([^"]+)"',
        ]
        
        for pattern in relationship_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for source, target in matches:
                if source.strip() != target.strip() and len(source.strip()) > 1 and len(target.strip()) > 1:
                    relationships.append({
                        "source": source.strip(),
                        "target": target.strip(),
                        "relation": "RELATED_TO",
                        "context": f"Extracted from pattern: {source} -> {target}",
                        "confidence": 0.5
                    })
                    print(f"[DEBUG] Fallback relationship: {source.strip()} -> {target.strip()}")
        
        return relationships
    
    def _extract_claims_array(self, text: str) -> List[str]:
        """Extract claims from malformed JSON response."""
        claims = []
        
        # Look for claims section
        claims_match = re.search(r'"claims":\s*\[(.*?)\]', text, re.DOTALL)
        if not claims_match:
            return claims
        
        claims_text = claims_match.group(1)
        
        # Extract quoted strings
        claim_matches = re.findall(r'"([^"]+)"', claims_text)
        claims.extend(claim_matches)
        
        return claims 