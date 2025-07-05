from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from neo4j_conn import get_neo4j_session
from sentence_transformers import SentenceTransformer
import numpy as np
import re

@dataclass
class SearchResult:
    """Represents a search result with metadata."""
    content: str
    source: str
    score: float
    result_type: str  # "vector", "graph", "keyword"
    metadata: Dict[str, Any] | None = None

@dataclass
class QueryAnalysis:
    """Analysis of a query for search optimization."""
    intent: str  # "factual", "analytical", "comparative"
    entities: List[str]
    keywords: List[str]
    reasoning_path: List[str] | None = None

class HybridRetriever:
    """Hybrid search system combining vector, graph, and keyword search."""
    
    def __init__(self, qdrant_url: str = "http://localhost:6333", collection_name: str = "documents"):
        """Initialize the hybrid retriever."""
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Initialize collection if it doesn't exist
        self._init_collection()
    
    def _init_collection(self):
        """Initialize Qdrant collection for document embeddings."""
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_model.get_sentence_embedding_dimension(),
                        distance=Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            print(f"Warning: Could not initialize Qdrant collection: {e}")
            print("Qdrant collection will be created when first needed.")
    
    def add_document_chunks(self, chunks: List[Dict[str, Any]]):
        """Add document chunks to the vector store."""
        if not chunks:
            return
        
        # Ensure collection exists
        try:
            self._init_collection()
        except Exception as e:
            print(f"Could not initialize collection for adding chunks: {e}")
            return
        
        # Prepare points for Qdrant
        points = []
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = self.embedding_model.encode(chunk["text"]).tolist()
            
            # Create point
            point = PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "chunk_id": chunk.get("chunk_id", f"chunk_{i}"),
                    "source_file": chunk.get("source_file", "unknown"),
                    "metadata": chunk.get("metadata", {})
                }
            )
            points.append(point)
        
        # Upload to Qdrant
        try:
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            print(f"Added {len(points)} chunks to vector store")
        except Exception as e:
            print(f"Error adding chunks to vector store: {e}")
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze query to determine intent and extract entities/keywords."""
        # Simple intent classification
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["what", "how", "why", "when", "where"]):
            intent = "factual"
        elif any(word in query_lower for word in ["compare", "difference", "versus", "vs"]):
            intent = "comparative"
        elif any(word in query_lower for word in ["analyze", "explain", "describe", "show"]):
            intent = "analytical"
        else:
            intent = "factual"
        
        # Extract potential entities (simple heuristic)
        entities = []
        # Look for capitalized words that might be entities
        words = query.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word)
        
        # Extract keywords
        keywords = [word.lower() for word in re.findall(r'\b\w+\b', query.lower()) 
                   if len(word) > 3 and word not in ["what", "how", "why", "when", "where", "the", "and", "for", "with"]]
        
        return QueryAnalysis(
            intent=intent,
            entities=entities,
            keywords=keywords,
            reasoning_path=None
        )
    
    def vector_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Perform vector similarity search."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k
            )
            
            # Convert to SearchResult objects
            results = []
            for result in search_result:
                search_result_obj = SearchResult(
                    content=result.payload["text"],
                    source=result.payload["source_file"],
                    score=result.score,
                    result_type="vector",
                    metadata=result.payload.get("metadata", {})
                )
                results.append(search_result_obj)
            
            return results
            
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []
    
    def graph_search(self, query: str, entities: List[str], depth: int = 2) -> List[SearchResult]:
        """Perform graph traversal search from extracted entities."""
        try:
            with get_neo4j_session() as session:
                results = []
                
                for entity in entities:
                    # Find entity and expand from it
                    query_cypher = f"""
                    MATCH (e:Entity {{name: $entity_name}})
                    OPTIONAL MATCH path = (e)-[*1..{depth}]-(related)
                    RETURN e, related, path
                    LIMIT 10
                    """
                    
                    result = session.run(query_cypher, entity_name=entity)
                    
                    for record in result:
                        if record["e"]:
                            # Add the entity itself
                            entity_node = record["e"]
                            results.append(SearchResult(
                                content=f"Entity: {entity_node['name']} ({entity_node.get('type', 'UNKNOWN')})",
                                source="graph",
                                score=1.0,
                                result_type="graph",
                                metadata={"entity_type": entity_node.get("type"), "entity_name": entity_node["name"]}
                            ))
                        
                        if record["related"]:
                            # Add related entities
                            related_node = record["related"]
                            results.append(SearchResult(
                                content=f"Related: {related_node['name']} ({related_node.get('type', 'UNKNOWN')})",
                                source="graph",
                                score=0.8,
                                result_type="graph",
                                metadata={"entity_type": related_node.get("type"), "entity_name": related_node["name"]}
                            ))
                
                return results
                
        except Exception as e:
            print(f"Error in graph search: {e}")
            return []
    
    def keyword_search(self, query: str, keywords: List[str]) -> List[SearchResult]:
        """Perform keyword-based search."""
        try:
            # Simple keyword matching in vector store payload
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=[0] * self.embedding_model.get_sentence_embedding_dimension(),  # Dummy vector
                limit=50,  # Get more results for keyword filtering
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="text",
                            match=MatchValue(value=keyword)
                        ) for keyword in keywords[:3]  # Limit to first 3 keywords
                    ]
                ) if keywords else None
            )
            
            results = []
            for result in search_result:
                # Calculate keyword match score
                text_lower = result.payload["text"].lower()
                keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
                score = keyword_matches / len(keywords) if keywords else 0.5
                
                search_result_obj = SearchResult(
                    content=result.payload["text"],
                    source=result.payload["source_file"],
                    score=score,
                    result_type="keyword",
                    metadata=result.payload.get("metadata", {})
                )
                results.append(search_result_obj)
            
            return results[:10]  # Return top 10
            
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return []
    
    def retrieve(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Main hybrid retrieval method."""
        # Step 1: Analyze query
        analysis = self.analyze_query(query)
        
        # Step 2: Perform different types of search
        vector_results = self.vector_search(query, top_k=top_k)
        graph_results = self.graph_search(query, analysis.entities, depth=2)
        keyword_results = self.keyword_search(query, analysis.keywords)
        
        # Step 3: Combine and rerank results
        all_results = vector_results + graph_results + keyword_results
        
        # Simple reranking: prefer vector results, then graph, then keyword
        for result in all_results:
            if result.result_type == "vector":
                result.score *= 1.2
            elif result.result_type == "graph":
                result.score *= 1.1
            # keyword results keep original score
        
        # Sort by score and return top_k
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:top_k]
    
    def multi_hop_reasoning(self, query: str) -> List[SearchResult]:
        """Perform multi-hop reasoning for complex queries."""
        analysis = self.analyze_query(query)
        
        if analysis.intent == "analytical":
            # For analytical queries, use graph traversal with multiple hops
            return self.graph_search(query, analysis.entities, depth=3)
        else:
            # For other queries, use standard hybrid retrieval
            return self.retrieve(query)
    
    def clear_vector_store(self):
        """Clear all data from the vector store."""
        try:
            # Get all point IDs first
            search_result = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=10000  # Get all points
            )
            
            if search_result[0]:  # If there are points to delete
                point_ids = [point.id for point in search_result[0]]
                
                # Delete the points using the correct selector format
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector={"points": point_ids}
                )
                print(f"Cleared {len(point_ids)} points from vector store collection: {self.collection_name}")
            else:
                print(f"No points to clear in vector store collection: {self.collection_name}")
                
        except Exception as e:
            print(f"Error clearing vector store: {e}")
            # Try alternative method - delete collection and recreate
            try:
                print("Attempting to delete and recreate collection...")
                self.qdrant_client.delete_collection(self.collection_name)
                self._init_collection()
                print(f"Successfully deleted and recreated collection: {self.collection_name}")
            except Exception as e2:
                print(f"Failed to delete/recreate collection: {e2}")
                raise
    
    def remove_document_from_vector_store(self, document_name: str) -> int:
        """Remove all chunks for a specific document from the vector store."""
        try:
            # Find all points for this document
            search_result = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="source_file",
                            match=MatchValue(value=document_name)
                        )
                    ]
                ),
                limit=1000  # Adjust based on expected chunk count
            )
            
            if not search_result[0]:  # No points found
                return 0
            
            # Extract point IDs
            point_ids = [point.id for point in search_result[0]]
            
            # Delete the points
            if point_ids:
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector={"points": point_ids}
                )
                print(f"Removed {len(point_ids)} chunks for document: {document_name}")
                return len(point_ids)
            
            return 0
            
        except Exception as e:
            print(f"Error removing document from vector store: {e}")
            return 0
    
    def list_documents_in_vector_store(self) -> List[Dict[str, Any]]:
        """List all documents in the vector store."""
        try:
            # Get all points to extract unique document names
            search_result = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=1000
            )
            
            documents = {}
            for point in search_result[0]:
                source_file = point.payload.get("source_file", "unknown")
                if source_file not in documents:
                    documents[source_file] = {
                        "name": source_file,
                        "chunks": 0,
                        "last_updated": None
                    }
                documents[source_file]["chunks"] += 1
            
            return list(documents.values())
            
        except Exception as e:
            print(f"Error listing documents in vector store: {e}")
            return []
    
    def add_documents(self, chunks):
        """Add documents to the vector store."""
        # Convert DocumentChunk objects to dictionaries
        chunk_dicts = []
        for chunk in chunks:
            chunk_dict = {
                "text": chunk.text,
                "chunk_id": chunk.chunk_id,
                "source_file": chunk.source_file,
                "metadata": chunk.metadata or {}
            }
            chunk_dicts.append(chunk_dict)
        
        self.add_document_chunks(chunk_dicts)
    
    def clear_all(self):
        """Clear all data from the vector store."""
        self.clear_vector_store()
    
    def remove_document(self, document_name: str) -> bool:
        """Remove a document from the vector store."""
        try:
            removed_count = self.remove_document_from_vector_store(document_name)
            return removed_count > 0
        except Exception:
            return False
    
    def list_documents(self) -> List[str]:
        """List document names in the vector store."""
        try:
            documents = self.list_documents_in_vector_store()
            return [doc["name"] for doc in documents]
        except Exception:
            return [] 