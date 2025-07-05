from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
import json
import re
import os

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
    
    def __init__(self, model_name: str = "claude-3-sonnet-20240229", api_key: str | None = None):
        """Initialize the entity extractor with Claude."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.")
        
        self.llm = ChatAnthropic(
            model=model_name,
            temperature=0.1,
            max_tokens=2048,
            anthropic_api_key=self.api_key
        )
        
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
        """Extract entities and relationships from text using Claude."""
        
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
                    metadata={"domain": domain}
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
                    metadata={"domain": domain}
                )
                relationships.append(relationship)
            
            claims = result_data.get("claims", [])
            
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
        """Validate and clean extracted entities."""
        validated_entities = []
        
        for entity in entities:
            # Basic validation
            if not entity.name or len(entity.name.strip()) < 2:
                continue
            
            # Clean entity name
            entity.name = entity.name.strip()
            
            # Remove duplicates (simple exact match)
            if not any(e.name == entity.name and e.entity_type == entity.entity_type 
                      for e in validated_entities):
                validated_entities.append(entity)
        
        return validated_entities
    
    def validate_relationships(self, relationships: List[Relationship], entities: List[Entity]) -> List[Relationship]:
        """Validate relationships against known entities."""
        entity_names = {entity.name for entity in entities}
        validated_relationships = []
        
        for relationship in relationships:
            # Check if both source and target entities exist
            if (relationship.source in entity_names and 
                relationship.target in entity_names and
                relationship.source != relationship.target):
                validated_relationships.append(relationship)
        
        return validated_relationships
    
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