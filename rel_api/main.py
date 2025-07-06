from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import os
import numpy as np
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Relationship Extraction API",
    description="Relationship extraction API using GLiNER multitask model",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class RelationRequest(BaseModel):
    text: str
    relations: List[Dict[str, Any]]
    entity_labels: Optional[List[str]] = None
    threshold: float = 0.5

class RelationResponse(BaseModel):
    text: str
    relations: List[Dict[str, Any]]
    processing_time: float
    model_info: Dict[str, Any]

class BatchRelationRequest(BaseModel):
    texts: List[str]
    relations: List[Dict[str, Any]]
    entity_labels: Optional[List[str]] = None
    threshold: float = 0.5

class BatchRelationResponse(BaseModel):
    results: List[Dict[str, Any]]
    processing_time: float
    model_info: Dict[str, Any]

class EntityRequest(BaseModel):
    text: str
    labels: List[str]
    threshold: float = 0.5

# Global variables for model
gliner_model = None
gliner_pipeline = None
model_info = {}

def load_gliner_model():
    """Load the GLiNER model and pipeline."""
    global gliner_model, gliner_pipeline, model_info
    
    try:
        logger.info("Loading GLiNER model...")
        
        from gliner import GLiNER
        gliner_model = GLiNER.from_pretrained("knowledgator/gliner-multitask-large-v0.5")
        
        # Create the relationship extraction pipeline using utca
        try:
            from utca.core import RenameAttribute
            from utca.implementation.predictors import (
                GLiNERPredictor,
                GLiNERPredictorConfig
            )
            from utca.implementation.tasks import (
                GLiNER,
                GLiNERPreprocessor,
                GLiNERRelationExtraction,
                GLiNERRelationExtractionPreprocessor,
            )
            
            predictor = GLiNERPredictor(
                GLiNERPredictorConfig(
                    model_name="knowledgator/gliner-multitask-large-v0.5",
                    device="cpu",  # Use CPU for Docker compatibility
                )
            )
            
            gliner_pipeline = (
                GLiNER(
                    predictor=predictor,
                    preprocess=GLiNERPreprocessor(threshold=0.7)
                )
                | RenameAttribute("output", "entities")
                | GLiNERRelationExtraction(
                    predictor=predictor,
                    preprocess=(
                        GLiNERPreprocessor(threshold=0.5)
                        | GLiNERRelationExtractionPreprocessor()
                    )
                )
            )
            
            logger.info("✅ GLiNER pipeline created successfully")
            
        except ImportError as e:
            logger.warning(f"utca library not available, falling back to basic GLiNER: {e}")
            gliner_pipeline = None
        
        # Store model info
        model_info = {
            "model_name": "knowledgator/gliner-multitask-large-v0.5",
            "model_type": "gliner-multitask",
            "capabilities": [
                "Named Entity Recognition (NER)",
                "Relation Extraction", 
                "Summarization",
                "Sentiment Extraction",
                "Key-Phrase Extraction",
                "Question-answering",
                "Open Information Extraction"
            ],
            "supported_tasks": "Multi-task information extraction",
            "pipeline_available": gliner_pipeline is not None
        }
        
        logger.info("✅ GLiNER model loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to load GLiNER model: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize the GLiNER model on startup."""
    success = load_gliner_model()
    if not success:
        logger.error("Failed to initialize GLiNER model. Service may not function properly.")

@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Relationship Extraction API is running",
        "model": "knowledgator/gliner-multitask-large-v0.5",
        "endpoints": {
            "/extract-relations": "Single text relation extraction",
            "/extract-relations/batch": "Batch relation extraction",
            "/health": "Health check",
            "/model-info": "Model information"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    status = "healthy" if gliner_model is not None else "unhealthy"
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "model_loaded": gliner_model is not None
    }

@app.get("/model-info")
async def get_model_info():
    """Get information about the loaded model."""
    if gliner_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_info": model_info,
        "model_ready": gliner_model is not None
    }

def clean_entity_text(text: str) -> str:
    """Clean entity text by removing punctuation and normalizing."""
    import re
    
    # Remove leading/trailing punctuation
    text = text.strip()
    text = re.sub(r'^[^\w\s]+', '', text)  # Remove leading punctuation
    text = re.sub(r'[^\w\s]+$', '', text)  # Remove trailing punctuation
    
    # Remove common unwanted patterns
    text = re.sub(r'^\d+\.?\s*', '', text)  # Remove numbered lists
    text = re.sub(r'^[•\-*]\s*', '', text)  # Remove bullet points
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def is_valid_entity(text: str, entity_type: str, score: float) -> bool:
    """Check if an entity is valid based on various criteria."""
    
    # Clean the text
    cleaned_text = clean_entity_text(text)
    
    # Basic validation
    if not cleaned_text or len(cleaned_text) < 2:
        return False
    
    # Confidence threshold (higher for shorter entities)
    min_confidence = 0.7 if len(cleaned_text) <= 3 else 0.6
    if score < min_confidence:
        return False
    
    # Filter out common noise
    noise_patterns = [
        r'^\d+$',  # Just numbers
        r'^[a-z]$',  # Single letters
        r'^[A-Z]$',  # Single capital letters
        r'^\d+[a-zA-Z]$',  # Number + single letter
        r'^[a-zA-Z]\d+$',  # Letter + numbers
        r'^[^\w\s]+$',  # Only punctuation
        r'^(the|a|an|and|or|but|in|on|at|to|for|of|with|by|from|up|down|out|off|over|under|above|below|before|after|during|while|since|until|unless|if|then|else|when|where|why|how|what|which|who|whom|whose|that|this|these|those|it|its|they|them|their|we|us|our|you|your|he|him|his|she|her|hers|i|me|my|mine)$',  # Common words
    ]
    
    import re
    for pattern in noise_patterns:
        if re.match(pattern, cleaned_text.lower()):
            return False
    
    # Entity type specific validation
    if entity_type.lower() in ['person', 'organisation']:
        # Names should be at least 2 characters and not just numbers
        if len(cleaned_text) < 2 or cleaned_text.isdigit():
            return False
    
    return True

@app.post("/extract-relations", response_model=RelationResponse)
async def extract_relations(request: RelationRequest):
    """Extract relationships from text using GLiNER."""
    if gliner_model is None:
        raise HTTPException(status_code=503, detail="GLiNER model not loaded")
    
    try:
        start_time = datetime.now()
        
        # Use the utca pipeline for proper relationship extraction if available
        if gliner_pipeline is not None:
            logger.info("Using GLiNER pipeline for relationship extraction")
            
            # Convert the request relations to the format expected by the pipeline
            pipeline_relations = []
            for relation_def in request.relations:
                pipeline_relation = {
                    "relation": relation_def.get("relation", ""),
                    "pairs_filter": relation_def.get("pairs_filter", []),
                    "distance_threshold": relation_def.get("distance_threshold", 100)
                }
                pipeline_relations.append(pipeline_relation)
            
            # Run the pipeline
            pipeline_input = {
                "text": request.text,
                "labels": request.entity_labels or [],
                "relations": pipeline_relations
            }
            
            result = gliner_pipeline.run(pipeline_input)
            
            # Process the pipeline output
            processed_relations = []
            if "output" in result:
                for relation in result["output"]:
                    processed_relation = {
                        "source": relation.get("source", ""),
                        "target": relation.get("target", ""),
                        "label": relation.get("relation", ""),
                        "score": relation.get("score", 0.5),
                        "context": relation.get("context", ""),
                        "source_type": relation.get("source_type", "entity"),
                        "target_type": relation.get("target_type", "entity")
                    }
                    processed_relations.append(processed_relation)
            
        else:
            # Fallback to basic GLiNER entity extraction
            logger.info("Using basic GLiNER for entity extraction (no relationship pipeline available)")
            
            # Extract entities first
            raw_entities = gliner_model.predict_entities(
                request.text, 
                request.entity_labels or [], 
                threshold=request.threshold
            )
            
            # Filter and clean entities
            valid_entities = []
            for entity in raw_entities:
                cleaned_text = clean_entity_text(entity["text"])
                if is_valid_entity(cleaned_text, entity["label"], entity["score"]):
                    valid_entity = {
                        "text": cleaned_text,
                        "label": entity["label"],
                        "score": float(entity["score"]) if isinstance(entity["score"], np.floating) else entity["score"],
                        "start": entity.get("start", 0),
                        "end": entity.get("end", 0)
                    }
                    valid_entities.append(valid_entity)
            
            # Create simple relationships based on entity proximity
            processed_relations = []
            seen_relations = set()
            
            for relation_def in request.relations:
                relation_name = relation_def.get("relation", "")
                pairs_filter = relation_def.get("pairs_filter", [])
                
                for entity1 in valid_entities:
                    for entity2 in valid_entities:
                        if entity1 == entity2:
                            continue
                        
                        # Check if this pair matches the relation filter
                        entity1_type = entity1["label"].lower()
                        entity2_type = entity2["label"].lower()
                        
                        for filter_pair in pairs_filter:
                            if (entity1_type == filter_pair[0] and entity2_type == filter_pair[1]):
                                # Create a unique key for this relation
                                relation_key = f"{entity1['text']}:{entity2['text']}:{relation_name}"
                                if relation_key in seen_relations:
                                    continue
                                
                                # Simple proximity check
                                if entity1["text"] in request.text and entity2["text"] in request.text:
                                    combined_score = min(entity1.get("score", 0.5), entity2.get("score", 0.5))
                                    
                                    if combined_score >= 0.5:
                                        relation = {
                                            "source": entity1["text"],
                                            "target": entity2["text"],
                                            "label": relation_name,
                                            "score": combined_score,
                                            "context": f"{entity1['text']} {relation_name} {entity2['text']}",
                                            "source_type": entity1_type,
                                            "target_type": entity2_type
                                        }
                                        processed_relations.append(relation)
                                        seen_relations.add(relation_key)
                                break
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return RelationResponse(
            text=request.text,
            relations=processed_relations,
            processing_time=processing_time,
            model_info=model_info
        )
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Error processing relation extraction request: {e}\n{tb}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}\n{tb}")

@app.post("/extract-relations/batch", response_model=BatchRelationResponse)
async def extract_relations_batch(request: BatchRelationRequest):
    """Extract relationships from multiple texts in batch."""
    if gliner_model is None:
        raise HTTPException(status_code=503, detail="GLiNER model not loaded")
    
    try:
        start_time = datetime.now()
        results = []
        
        for i, text in enumerate(request.texts):
            try:
                # Prepare entity labels if provided
                labels = request.entity_labels or []
                
                # Extract relations using GLiNER
                relations = gliner_model.predict_entities(
                    text, 
                    labels, 
                    threshold=request.threshold
                )
                
                # Convert numpy types to native Python types
                processed_relations = []
                for relation in relations:
                    processed_relation = {
                        "text": relation["text"],
                        "label": relation["label"],
                        "score": float(relation["score"]) if isinstance(relation["score"], np.floating) else relation["score"],
                        "start": relation.get("start", 0),
                        "end": relation.get("end", 0)
                    }
                    processed_relations.append(processed_relation)
                
                results.append({
                    "text": text,
                    "relations": processed_relations,
                    "relation_count": len(processed_relations)
                })
                
            except Exception as e:
                logger.error(f"Error processing text {i}: {e}")
                results.append({
                    "text": text,
                    "relations": [],
                    "relation_count": 0,
                    "error": str(e)
                })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return BatchRelationResponse(
            results=results,
            processing_time=processing_time,
            model_info=model_info
        )
        
    except Exception as e:
        logger.error(f"Error processing batch relation extraction request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing batch: {str(e)}")

@app.post("/extract-entities")
async def extract_entities(request: EntityRequest):
    """Extract entities from text using GLiNER."""
    if gliner_model is None:
        raise HTTPException(status_code=503, detail="GLiNER model not loaded")
    
    try:
        start_time = datetime.now()
        
        # Extract entities using GLiNER
        raw_entities = gliner_model.predict_entities(request.text, request.labels, threshold=request.threshold)
        
        # Filter and clean entities
        processed_entities = []
        for entity in raw_entities:
            cleaned_text = clean_entity_text(entity["text"])
            if is_valid_entity(cleaned_text, entity["label"], entity["score"]):
                processed_entity = {
                    "text": cleaned_text,
                    "label": entity["label"],
                    "score": float(entity["score"]) if isinstance(entity["score"], np.floating) else entity["score"],
                    "start": entity.get("start", 0),
                    "end": entity.get("end", 0)
                }
                processed_entities.append(processed_entity)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "text": request.text,
            "entities": processed_entities,
            "entity_count": len(processed_entities),
            "processing_time": processing_time,
            "model_info": model_info
        }
        
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting entities: {str(e)}")

@app.get("/capabilities")
async def get_capabilities():
    """Get the list of capabilities that the model supports."""
    return {
        "capabilities": [
            "Named Entity Recognition (NER)",
            "Relation Extraction", 
            "Summarization",
            "Sentiment Extraction",
            "Key-Phrase Extraction",
            "Question-answering",
            "Open Information Extraction"
        ],
        "model": "knowledgator/gliner-multitask-large-v0.5",
        "description": "Multi-task information extraction model"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 