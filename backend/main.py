from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import os
import tempfile
import shutil
import json
import logging
from document_processor import DocumentProcessor, DocumentChunk
from enhanced_document_processor import EnhancedDocumentProcessor
from hybrid_retriever import HybridRetriever
from query_processor import QueryProcessor
from entity_extractor import EntityExtractor, Entity, Relationship
from knowledge_graph_builder import KnowledgeGraphBuilder
from graphrag_evaluator import GraphRAGEvaluator
from automated_test_suite import AutomatedTestSuite
from datetime import datetime
from pydantic import BaseModel
from ner_client import get_ner_client, extract_entities_from_text, extract_entities_from_chunks, is_ner_available
from rel_extractor import get_relationship_extractor
from enhanced_query_processor import EnhancedQueryProcessor
from entity_linker import EntityLinker
from graph_reasoner import GraphReasoner
from advanced_reasoning_engine import AdvancedReasoningEngine
from enhanced_entity_extractor import EnhancedEntityExtractor, get_enhanced_entity_extractor

logger = logging.getLogger(__name__)

app = FastAPI(title="Graph RAG System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize processors
document_processor = DocumentProcessor()
enhanced_processor = EnhancedDocumentProcessor()
hybrid_retriever = HybridRetriever(qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"))
query_processor = QueryProcessor()

# Initialize knowledge graph components
try:
    entity_extractor = EntityExtractor()
    knowledge_graph_builder = KnowledgeGraphBuilder()
    print("✅ Knowledge graph components initialized successfully")
except Exception as e:
    print(f"⚠️  Knowledge graph initialization failed: {e}")
    entity_extractor = None
    knowledge_graph_builder = None

# Initialize evaluation components
try:
    evaluator = GraphRAGEvaluator()
    test_suite = AutomatedTestSuite()
    print("✅ Evaluation components initialized successfully")
except Exception as e:
    print(f"⚠️  Evaluation components initialization failed: {e}")
    evaluator = None
    test_suite = None

# Initialize advanced reasoning components
advanced_reasoning_engine = AdvancedReasoningEngine()
enhanced_query_processor = EnhancedQueryProcessor()
entity_linker = EntityLinker()
graph_reasoner = GraphReasoner()

class AdvancedSearchRequest(BaseModel):
    query: str
    search_type: str = "hybrid"  # "vector", "graph", "keyword", "hybrid"
    top_k: int = 10
    domain: str | None = None
    filters: dict | None = None

class ExtractionRequest(BaseModel):
    text: str
    domain: str = "general"

@app.get("/")
def read_root():
    return {"message": "Graph RAG backend is running."}

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/process-document")
async def process_document(
    file: UploadFile = File(...),
    use_semantic_chunking: bool = True
):
    """Process a single document and return chunks."""
    try:
        # Save uploaded file temporarily
        filename = file.filename or "unknown"
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Process document
        if use_semantic_chunking:
            chunks = enhanced_processor.process_document_enhanced(temp_path)
        else:
            chunks = document_processor.process_document(temp_path)
        
        # Convert chunks to serializable format
        chunk_data = []
        for chunk in chunks:
            chunk_data.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "source_file": chunk.source_file,
                "page_number": chunk.page_number,
                "section_header": chunk.section_header,
                "chunk_index": chunk.chunk_index,
                "metadata": chunk.metadata
            })
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return {
            "filename": file.filename,
            "chunks": chunk_data,
            "total_chunks": len(chunk_data),
            "use_semantic_chunking": use_semantic_chunking
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        
        raise HTTPException(status_code=400, detail=f"Error processing document: {str(e)}")

@app.post("/process-documents-batch")
async def process_documents_batch(
    files: List[UploadFile] = File(...),
    use_semantic_chunking: bool = True
):
    """Process multiple documents in batch."""
    try:
        results = {}
        temp_files = []
        
        for file in files:
            # Save uploaded file temporarily
            filename = file.filename or "unknown"
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_path = temp_file.name
                temp_files.append(temp_path)
            
            # Process document
            if use_semantic_chunking:
                chunks = enhanced_processor.process_document_enhanced(temp_path)
            else:
                chunks = document_processor.process_document(temp_path)
            
            # Convert chunks to serializable format
            chunk_data = []
            for chunk in chunks:
                chunk_data.append({
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "source_file": chunk.source_file,
                    "page_number": chunk.page_number,
                    "section_header": chunk.section_header,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata
                })
            
            results[file.filename] = {
                "chunks": chunk_data,
                "total_chunks": len(chunk_data)
            }
        
        # Clean up temporary files
        for temp_path in temp_files:
            try:
                os.unlink(temp_path)
            except:
                pass
        
        return {
            "results": results,
            "total_files": len(files),
            "use_semantic_chunking": use_semantic_chunking
        }
        
    except Exception as e:
        # Clean up temporary files
        for temp_path in temp_files:
            try:
                os.unlink(temp_path)
            except:
                pass
        
        raise HTTPException(status_code=400, detail=f"Error processing documents: {str(e)}")

@app.get("/supported-formats")
def get_supported_formats():
    """Get list of supported document formats."""
    return {
        "supported_formats": [
            ".pdf", ".docx", ".txt", ".html", ".csv", ".json"
        ],
        "features": {
            "semantic_chunking": True,
            "metadata_extraction": True,
            "content_type_classification": True,
            "structure_preservation": True
        }
    }

@app.post("/search")
async def search_documents(query: str = Form(...), top_k: int = Form(10)):
    """Search documents using hybrid retrieval and generate answer using LLM."""
    try:
        # Process query
        query_analysis = query_processor.get_query_analysis(query)
        
        # Perform hybrid search
        results = hybrid_retriever.retrieve(query, top_k=top_k)
        
        # Convert results to serializable format
        search_results = []
        for result in results:
            search_results.append({
                "content": result.content,
                "source": result.source,
                "score": result.score,
                "metadata": result.metadata
            })
        
        # Generate answer using LLM if we have results and entity_extractor (which has the LLM)
        generated_answer = ""
        if results and entity_extractor:
            # Prepare context from retrieved documents
            context_chunks = []
            for result in results[:5]:  # Use top 5 results for context
                context_chunks.append(f"Source: {result.source}\nContent: {result.content}")
            
            context = "\n\n".join(context_chunks)
            
            # Create RAG prompt
            rag_prompt = f"""You are a helpful assistant that answers questions based on the provided context. 
Use the following context to answer the user's question. If the context doesn't contain enough information to answer the question, say so clearly.

Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. Include specific details and cite sources when possible."""

            try:
                # Use the LLM from entity_extractor to generate answer
                response = entity_extractor.llm.invoke(rag_prompt)
                generated_answer = response.content if hasattr(response, 'content') else str(response)
            except Exception as llm_error:
                print(f"LLM generation error: {llm_error}")
                generated_answer = f"Found {len(results)} relevant results, but could not generate a comprehensive answer due to an error."
        
        # If no results or no LLM, provide a basic response
        if not generated_answer:
            if not results:
                generated_answer = "No relevant information found in the documents. Please try a different query or upload more documents."
            else:
                generated_answer = f"Found {len(results)} relevant results for '{query}'. {results[0].content[:200]}..." if results else "No results found."
        
        return {
            "answer": generated_answer,
            "results": search_results,
            "total_results": len(search_results),
            "query_analysis": query_analysis,
            "sources": list(set([result["source"] for result in search_results]))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/search-advanced")
async def advanced_search(request: AdvancedSearchRequest = Body(...)):
    """Advanced search with different search strategies and LLM answer generation."""
    try:
        # Process query
        query_analysis = query_processor.get_query_analysis(request.query)
        search_type = request.search_type
        top_k = request.top_k
        entities = query_analysis["entities"] if "entities" in query_analysis else []
        keywords = query_analysis["keywords"] if "keywords" in query_analysis else []
        # Perform search based on type
        if search_type == "vector":
            results = hybrid_retriever.vector_search(request.query, top_k=top_k)
        elif search_type == "graph":
            results = hybrid_retriever.graph_search(request.query, entities, depth=2)
        elif search_type == "keyword":
            results = hybrid_retriever.keyword_search(request.query, keywords)[:top_k]
        else:  # hybrid
            results = hybrid_retriever.retrieve(request.query, top_k=top_k)
        # Convert results to serializable format
        search_results = []
        for result in results:
            search_results.append({
                "content": result.content,
                "source": result.source,
                "score": result.score,
                "metadata": result.metadata
            })
        # LLM answer generation (like /search)
        generated_answer = ""
        if results and entity_extractor:
            # Prepare context from retrieved documents
            context_chunks = []
            for result in results[:5]:  # Use top 5 results for context
                context_chunks.append(f"Source: {result.source}\nContent: {result.content}")
            context = "\n\n".join(context_chunks)

            # --- Knowledge Graph Injection ---
            print(f"[DEBUG] Extracted entities: {entities}")
            # Use LLM analysis entities if main extraction is empty or generic
            llm_entities = query_analysis.get("llm_analysis", {}).get("entities", [])
            use_entities = entities
            # If entities is empty or only contains generic words, use LLM entities
            if not entities or all(e.get("name", "").lower() in ["what", "which", "who", "where", "when", "how"] for e in entities if isinstance(e, dict)):
                use_entities = llm_entities
                print(f"[DEBUG] Falling back to LLM analysis entities: {llm_entities}")
            kg_summaries = []
            if knowledge_graph_builder and use_entities:
                for ent in use_entities:
                    ent_name = ent["name"] if isinstance(ent, dict) and "name" in ent else str(ent)
                    rels = knowledge_graph_builder.get_direct_relationships(ent_name)
                    if not rels:
                        # Try case-insensitive match if not found
                        all_nodes = list(knowledge_graph_builder.graph.nodes())
                        print(f"[DEBUG] No relationships for '{ent_name}'. All graph nodes: {all_nodes}")
                        ent_name_ci = next((n for n in all_nodes if n.lower() == ent_name.lower()), None)
                        if ent_name_ci:
                            print(f"[DEBUG] Found case-insensitive match for '{ent_name}': '{ent_name_ci}'")
                            rels = knowledge_graph_builder.get_direct_relationships(ent_name_ci)
                    if rels:
                        rel_str = ", ".join([f"{target} ({rel_type})" for target, rel_type in rels])
                        summary = f"=== KNOWLEDGE GRAPH RELATIONSHIPS ===\n{ent_name} is connected to: {rel_str}."
                        print(f"[DEBUG] Using relationships for '{ent_name}': {rel_str}")
                        kg_summaries.append(summary)
                    else:
                        print(f"[DEBUG] No relationships found for '{ent_name}' even after case-insensitive check.")
            kg_context = "\n".join(kg_summaries)
            print(f"[DEBUG] KG context summary: {kg_context}")
            # Prepend KG context to LLM context if available
            full_context = (kg_context + "\n\n" if kg_context else "") + context
            rag_prompt = f"""You are a helpful assistant that answers questions based on the provided context. \
Use the following context to answer the user's question. If the context doesn't contain enough information to answer the question, say so clearly.\n\nContext:\n{full_context}\n\nQuestion: {request.query}\n\nPlease provide a comprehensive answer based on the context above. Include specific details and cite sources when possible."""
            print(f"[DEBUG] Final LLM prompt:\n{rag_prompt}")
            try:
                response = entity_extractor.llm.invoke(rag_prompt)
                generated_answer = response.content if hasattr(response, 'content') else str(response)
            except Exception as llm_error:
                print(f"LLM generation error: {llm_error}")
                generated_answer = f"Found {len(results)} relevant results, but could not generate a comprehensive answer due to an error."
        # If no results or no LLM, provide a basic response
        if not generated_answer:
            if not results:
                generated_answer = "No relevant information found in the documents. Please try a different query or upload more documents."
            else:
                generated_answer = f"Found {len(results)} relevant results for '{request.query}'. {results[0].content[:200]}..." if results else "No results found."
        return {
            "answer": generated_answer,
            "results": search_results,
            "total_results": len(search_results),
            "search_type": search_type,
            "query_analysis": query_analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advanced search error: {str(e)}")

@app.post("/ingest-documents")
async def ingest_documents(
    files: List[UploadFile] = File(...),
    domain: str = "general",
    build_knowledge_graph: bool = True
):
    """Ingest documents into the system with knowledge graph building."""
    try:
        results = {}
        temp_files = []
        
        for file in files:
            # Save uploaded file temporarily
            filename = file.filename or "unknown"
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_path = temp_file.name
                temp_files.append(temp_path)
            
            # Process document with enhanced processor
            chunks = enhanced_processor.process_document_enhanced(temp_path)
            
            # Add to vector store
            hybrid_retriever.add_documents(chunks)
            
            # Build knowledge graph if enabled
            if build_knowledge_graph and entity_extractor and knowledge_graph_builder:
                print(f"🔍 Extracting entities and relationships from {filename} ({len(chunks)} chunks)...")
                
                # Extract entities and relationships from chunks with batching
                all_entities = []
                all_relationships = []
                
                # Process chunks in batches to avoid overwhelming the API
                batch_size = 5  # Process 5 chunks at a time
                successful_extractions = 0
                failed_extractions = 0
                
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i:i + batch_size]
                    batch_num = (i // batch_size) + 1
                    total_batches = (len(chunks) + batch_size - 1) // batch_size
                    
                    print(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
                    
                    for chunk_idx, chunk in enumerate(batch):
                        try:
                            # Add timeout handling for individual chunk processing
                            import signal
                            
                            def timeout_handler(signum, frame):
                                raise TimeoutError("Entity extraction timeout")
                            
                            # Set timeout for 30 seconds per chunk
                            signal.signal(signal.SIGALRM, timeout_handler)
                            signal.alarm(30)
                            
                            extraction_result = entity_extractor.extract_entities_and_relations(
                                chunk.text, domain=domain
                            )
                            
                            # Cancel timeout
                            signal.alarm(0)
                            
                            # Validate entities and relationships
                            validated_entities = entity_extractor.validate_entities(extraction_result.entities)
                            validated_relationships = entity_extractor.validate_relationships(
                                extraction_result.relationships, validated_entities
                            )
                            
                            all_entities.extend(validated_entities)
                            all_relationships.extend(validated_relationships)
                            successful_extractions += 1
                            
                            if validated_entities or validated_relationships:
                                print(f"  ✅ Chunk {i + chunk_idx + 1}: {len(validated_entities)} entities, {len(validated_relationships)} relationships")
                            
                        except (TimeoutError, Exception) as e:
                            signal.alarm(0)  # Cancel timeout
                            failed_extractions += 1
                            print(f"  ⚠️  Chunk {i + chunk_idx + 1} failed: {str(e)[:100]}...")
                            continue
                
                print(f"🔍 Completed extraction: {successful_extractions} successful, {failed_extractions} failed")
                print(f"🔍 Total extracted: {len(all_entities)} entities and {len(all_relationships)} relationships from {filename}")
                
                # Build knowledge graph
                if all_entities:
                    print(f"🕸️  Building knowledge graph with {len(all_entities)} entities and {len(all_relationships)} relationships")
                    knowledge_graph_builder.build_graph(all_entities, all_relationships, domain=domain)
                else:
                    print("⚠️  No entities extracted, skipping knowledge graph building")
            
            # Convert chunks to serializable format
            chunk_data = []
            for chunk in chunks:
                chunk_data.append({
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "source_file": chunk.source_file,
                    "page_number": chunk.page_number,
                    "section_header": chunk.section_header,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata
                })
            
            results[file.filename] = {
                "chunks": chunk_data,
                "total_chunks": len(chunk_data),
                "entities": len(all_entities) if 'all_entities' in locals() else 0,
                "relationships": len(all_relationships) if 'all_relationships' in locals() else 0
            }
        
        # Clean up temporary files
        for temp_path in temp_files:
            try:
                os.unlink(temp_path)
            except:
                pass
        
        return {
            "results": results,
            "total_files": len(files),
            "domain": domain,
            "build_knowledge_graph": build_knowledge_graph
        }
        
    except Exception as e:
        # Clean up temporary files
        for temp_path in temp_files:
            try:
                os.unlink(temp_path)
            except:
                pass
        
        raise HTTPException(status_code=400, detail=f"Error ingesting documents: {str(e)}")

@app.get("/knowledge-graph/stats")
async def get_knowledge_graph_stats(domain: str | None = None):
    """Get knowledge graph statistics, optionally filtered by domain."""
    try:
        if not knowledge_graph_builder:
            raise HTTPException(status_code=503, detail="Knowledge graph not available")
        
        stats = knowledge_graph_builder.get_graph_stats(domain)
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting graph stats: {str(e)}")

@app.get("/knowledge-graph/domains")
async def get_available_domains():
    """Get list of available domains in the knowledge graph."""
    try:
        if not knowledge_graph_builder:
            raise HTTPException(status_code=503, detail="Knowledge graph not available")
        
        domains = knowledge_graph_builder.get_available_domains()
        return {"domains": domains, "count": len(domains)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting domains: {str(e)}")

@app.get("/knowledge-graph/domain-stats")
async def get_domain_statistics():
    """Get statistics for each domain in the knowledge graph."""
    try:
        if not knowledge_graph_builder:
            raise HTTPException(status_code=503, detail="Knowledge graph not available")
        
        domain_stats = knowledge_graph_builder.get_domain_statistics()
        return domain_stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting domain statistics: {str(e)}")

@app.get("/knowledge-graph/export")
async def export_knowledge_graph(format: str = "json", domain: str | None = None):
    """Export knowledge graph data, optionally filtered by domain."""
    try:
        if not knowledge_graph_builder:
            raise HTTPException(status_code=503, detail="Knowledge graph not available")
        
        if format == "json":
            graph_data = knowledge_graph_builder.export_graph_json(domain)
            return graph_data
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting graph: {str(e)}")

@app.post("/add-to-vector-store")
async def add_to_vector_store_legacy(files: List[UploadFile] = File(...)):
    """Legacy endpoint for adding documents to vector store only."""
    return await ingest_documents(files=files, build_knowledge_graph=False)

@app.delete("/clear-all")
async def clear_all_data():
    """Clear all data from vector store and knowledge graph."""
    try:
        # Clear vector store
        hybrid_retriever.clear_all()
        
        # Clear knowledge graph
        if knowledge_graph_builder:
            knowledge_graph_builder.clear_graph()
        
        return {
            "message": "All data cleared successfully",
            "vector_store_cleared": True,
            "knowledge_graph_cleared": knowledge_graph_builder is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")

@app.delete("/documents/{document_name}")
async def remove_document(document_name: str):
    """Remove a specific document from the system."""
    try:
        # Remove from vector store
        removed_from_vector = hybrid_retriever.remove_document(document_name)
        
        # Remove from knowledge graph
        removed_from_graph = False
        if knowledge_graph_builder:
            removed_from_graph = knowledge_graph_builder.remove_document_entities(document_name)
        
        return {
            "message": f"Document '{document_name}' removed successfully",
            "removed_from_vector_store": removed_from_vector,
            "removed_from_knowledge_graph": removed_from_graph
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing document: {str(e)}")

@app.get("/documents/list")
async def list_documents():
    """List all documents in the system."""
    try:
        # Get documents from vector store
        vector_documents = hybrid_retriever.list_documents()
        
        # Get documents from knowledge graph
        graph_documents = []
        if knowledge_graph_builder:
            graph_documents = knowledge_graph_builder.list_documents()
        
        # Combine and deduplicate
        all_documents = list(set(vector_documents + graph_documents))
        
        return {
            "documents": all_documents,
            "total_documents": len(all_documents),
            "vector_store_documents": len(vector_documents),
            "knowledge_graph_documents": len(graph_documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

# Evaluation Framework Endpoints

@app.post("/evaluate/entity-extraction")
async def evaluate_entity_extraction(
    test_documents: List[str] = Body(...),
    ground_truth: Dict[str, List[Dict[str, Any]]] = Body(...)
):
    """Evaluate entity extraction accuracy."""
    try:
        if not evaluator:
            raise HTTPException(status_code=500, detail="Evaluation framework not available")
        
        results = evaluator.evaluate_entity_extraction(test_documents, ground_truth)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating entity extraction: {str(e)}")

@app.post("/evaluate/query-responses")
async def evaluate_query_responses(
    test_queries: List[str] = Body(...),
    expected_answers: List[str] = Body(...)
):
    """Evaluate query response accuracy."""
    try:
        if not evaluator:
            raise HTTPException(status_code=500, detail="Evaluation framework not available")
        
        results = evaluator.evaluate_query_responses(test_queries, expected_answers)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating query responses: {str(e)}")

@app.get("/evaluate/graph-completeness")
async def evaluate_graph_completeness():
    """Evaluate knowledge graph completeness."""
    try:
        if not evaluator:
            raise HTTPException(status_code=500, detail="Evaluation framework not available")
        
        results = evaluator.evaluate_graph_completeness()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating graph completeness: {str(e)}")

@app.post("/evaluate/retrieval-relevance")
async def evaluate_retrieval_relevance(
    test_queries: List[str] = Body(...),
    relevance_scores: List[float] = Body(...)
):
    """Evaluate retrieval relevance."""
    try:
        if not evaluator:
            raise HTTPException(status_code=500, detail="Evaluation framework not available")
        
        results = evaluator.evaluate_retrieval_relevance(test_queries, relevance_scores)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating retrieval relevance: {str(e)}")

@app.post("/evaluate/comprehensive")
async def evaluate_comprehensive(
    test_data: Dict[str, Any] = Body(...)
):
    """Run comprehensive evaluation."""
    try:
        if not evaluator:
            raise HTTPException(status_code=500, detail="Evaluation framework not available")
        
        # Run all evaluation types
        results = {}
        
        if 'entity_extraction' in test_data:
            results['entity_extraction'] = evaluator.evaluate_entity_extraction(
                test_data['entity_extraction']['documents'],
                test_data['entity_extraction']['ground_truth']
            )
        
        if 'query_responses' in test_data:
            results['query_responses'] = evaluator.evaluate_query_responses(
                test_data['query_responses']['queries'],
                test_data['query_responses']['expected_answers']
            )
        
        results['graph_completeness'] = evaluator.evaluate_graph_completeness()
        
        if 'retrieval_relevance' in test_data:
            results['retrieval_relevance'] = evaluator.evaluate_retrieval_relevance(
                test_data['retrieval_relevance']['queries'],
                test_data['retrieval_relevance']['relevance_scores']
            )
        
        # Generate comprehensive report
        report = evaluator.generate_evaluation_report(results)
        
        return {
            "results": results,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running comprehensive evaluation: {str(e)}")

# Automated Test Suite Endpoints

@app.post("/test/run-unit-tests")
async def run_unit_tests():
    """Run unit tests."""
    try:
        if not test_suite:
            raise HTTPException(status_code=500, detail="Test suite not available")
        
        results = test_suite.run_unit_tests()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running unit tests: {str(e)}")

@app.post("/test/run-integration-tests")
async def run_integration_tests():
    """Run integration tests."""
    try:
        if not test_suite:
            raise HTTPException(status_code=500, detail="Test suite not available")
        
        results = test_suite.run_integration_tests()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running integration tests: {str(e)}")

@app.post("/test/run-performance-tests")
async def run_performance_tests():
    """Run performance tests."""
    try:
        if not test_suite:
            raise HTTPException(status_code=500, detail="Test suite not available")
        
        results = test_suite.run_performance_tests()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running performance tests: {str(e)}")

@app.post("/test/run-quality-tests")
async def run_quality_tests():
    """Run quality tests."""
    try:
        if not test_suite:
            raise HTTPException(status_code=500, detail="Test suite not available")
        
        results = test_suite.run_quality_tests()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running quality tests: {str(e)}")

@app.post("/test/run-comprehensive-tests")
async def run_comprehensive_tests():
    """Run comprehensive test suite."""
    try:
        if not test_suite:
            raise HTTPException(status_code=500, detail="Test suite not available")
        
        results = test_suite.run_comprehensive_tests()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running comprehensive tests: {str(e)}")

@app.get("/test/reports")
async def get_test_reports():
    """Get generated test reports."""
    try:
        import os
        
        reports = {}
        
        if os.path.exists('test_results.json'):
            with open('test_results.json', 'r') as f:
                import json
                reports['test_results'] = json.load(f)
        
        if os.path.exists('test_summary.txt'):
            with open('test_summary.txt', 'r') as f:
                reports['test_summary'] = f.read()
        
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving test reports: {str(e)}")

# NER Integration Endpoints

@app.get("/ner/status")
async def get_ner_status():
    """Check if NER API is available."""
    try:
        available = is_ner_available()
        client = get_ner_client()
        
        if client:
            model_info = client.get_model_info()
        else:
            model_info = None
        
        return {
            "ner_available": available,
            "model_info": model_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking NER status: {str(e)}")

@app.post("/ner/extract")
async def extract_entities_from_text_endpoint(text: str = Body(...)):
    """Extract entities from text using the NER API."""
    try:
        if not is_ner_available():
            raise HTTPException(status_code=503, detail="NER API is not available")
        
        entities = extract_entities_from_text(text)
        
        return {
            "text": text,
            "entities": entities,
            "entity_count": len(entities),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting entities: {str(e)}")

@app.post("/ner/extract-batch")
async def extract_entities_batch_endpoint(texts: List[str] = Body(...)):
    """Extract entities from multiple texts using the NER API."""
    try:
        if not is_ner_available():
            raise HTTPException(status_code=503, detail="NER API is not available")
        
        entity_lists = extract_entities_from_chunks(texts)
        
        results = []
        for i, (text, entities) in enumerate(zip(texts, entity_lists)):
            results.append({
                "text": text,
                "entities": entities,
                "entity_count": len(entities)
            })
        
        return {
            "results": results,
            "total_texts": len(texts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting entities in batch: {str(e)}")

@app.post("/process-document-with-ner")
async def process_document_with_ner(
    file: UploadFile = File(...),
    use_semantic_chunking: bool = True,
    extract_entities: bool = True
):
    """Process a document and extract entities from chunks."""
    try:
        # Save uploaded file temporarily
        filename = file.filename or "unknown"
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        # Process document
        if use_semantic_chunking:
            chunks = enhanced_processor.process_document_enhanced(temp_path)
        else:
            chunks = document_processor.process_document(temp_path)
        
        # Convert chunks to serializable format
        chunk_data = []
        for chunk in chunks:
            chunk_data.append({
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "source_file": chunk.source_file,
                "page_number": chunk.page_number,
                "section_header": chunk.section_header,
                "chunk_index": chunk.chunk_index,
                "metadata": chunk.metadata
            })
        
        # Extract entities if requested and NER is available
        if extract_entities and is_ner_available():
            chunk_texts = [chunk["text"] for chunk in chunk_data]
            entity_lists = extract_entities_from_chunks(chunk_texts)
            
            # Add entities to chunk data
            for i, (chunk, entities) in enumerate(zip(chunk_data, entity_lists)):
                chunk["entities"] = entities
                chunk["entity_count"] = len(entities)
        else:
            # Add empty entities if NER is not available
            for chunk in chunk_data:
                chunk["entities"] = []
                chunk["entity_count"] = 0
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return {
            "filename": file.filename,
            "chunks": chunk_data,
            "total_chunks": len(chunk_data),
            "use_semantic_chunking": use_semantic_chunking,
            "ner_available": is_ner_available(),
            "entities_extracted": extract_entities and is_ner_available()
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        
        raise HTTPException(status_code=400, detail=f"Error processing document: {str(e)}")

# Entity and Relationship Extraction Endpoints

@app.post("/extract-entities-relations")
async def extract_entities_and_relations(request: ExtractionRequest):
    """Extract entities and relationships from text using integrated GLiNER system."""
    try:
        if not entity_extractor:
            raise HTTPException(status_code=503, detail="Entity extractor not available")
        
        # Use the integrated entity extractor which now uses GLiNER for relationships
        result = entity_extractor.extract_entities_and_relations(request.text, request.domain)
        
        # Convert to JSON-serializable format
        entities = []
        for entity in result.entities:
            entities.append({
                "name": entity.name,
                "type": entity.entity_type,
                "description": entity.description,
                "confidence": entity.confidence,
                "metadata": entity.metadata
            })
        
        relationships = []
        for rel in result.relationships:
            relationships.append({
                "source": rel.source,
                "target": rel.target,
                "relation": rel.relation_type,
                "context": rel.context,
                "confidence": rel.confidence,
                "metadata": rel.metadata
            })
        
        return {
            "text": request.text,
            "domain": request.domain,
            "entities": entities,
            "relationships": relationships,
            "claims": result.claims,
            "entity_count": len(entities),
            "relationship_count": len(relationships),
            "extraction_method": "integrated_gliner",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting entities and relationships: {str(e)}")

@app.get("/rel/status")
async def get_rel_status():
    """Check if GLiNER relationship extraction API is available."""
    try:
        rel_extractor = get_relationship_extractor()
        available = rel_extractor.is_available()
        
        if available:
            model_info = rel_extractor.get_model_info()
            capabilities = rel_extractor.get_capabilities()
        else:
            model_info = None
            capabilities = None
        
        return {
            "rel_available": available,
            "model_info": model_info,
            "capabilities": capabilities,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking GLiNER status: {str(e)}")

@app.post("/rel/extract")
async def extract_relationships_from_text(
    text: str = Body(...),
    relations: List[Dict[str, Any]] = Body(default=[]),
    entity_labels: List[str] = Body(default=[]),
    threshold: float = 0.5
):
    """Extract relationships from text using GLiNER API."""
    try:
        rel_extractor = get_relationship_extractor()
        if not rel_extractor.is_available():
            raise HTTPException(status_code=503, detail="GLiNER API is not available")
        
        # Use default relations if none provided
        if not relations:
            relations = [
                {"relation": "founder", "pairs_filter": [("organisation", "founder")]},
                {"relation": "inception date", "pairs_filter": [("organisation", "date")]},
                {"relation": "held position", "pairs_filter": [("founder", "position")]},
                {"relation": "works for", "pairs_filter": [("person", "organisation")]},
                {"relation": "located in", "pairs_filter": [("organisation", "location"), ("person", "location")]},
                {"relation": "acquired", "pairs_filter": [("organisation", "organisation")]},
                {"relation": "product", "pairs_filter": [("organisation", "product")]},
                {"relation": "subsidiary", "pairs_filter": [("organisation", "organisation")]},
                {"relation": "industry", "pairs_filter": [("organisation", "industry")]},
            ]
        
        result = rel_extractor.extract_relations(
            text=text,
            relations=relations,
            entity_labels=entity_labels,
            threshold=threshold
        )
        
        return {
            "text": text,
            "relations": result.get("relations", []),
            "relation_count": len(result.get("relations", [])),
            "processing_time": result.get("processing_time", 0),
            "model_info": result.get("model_info", {}),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting relationships: {str(e)}")

# Enhanced Query Processing Endpoints

@app.post("/query/enhanced")
async def enhanced_query_processing(request: AdvancedSearchRequest):
    """Process queries with graph-based reasoning and entity linking."""
    try:
        # Get all entities and relationships from the knowledge graph
        # This would typically come from your Neo4j database
        # For now, we'll use a placeholder - you'll need to implement this
        entities = []  # TODO: Get from Neo4j
        relationships = []  # TODO: Get from Neo4j
        
        # Process the query with enhanced reasoning
        result = enhanced_query_processor.process_query(request.query, entities, relationships)
        
        return {
            "query": result.query,
            "results": result.results,
            "reasoning_paths": [
                {
                    "source": path.source,
                    "target": path.target,
                    "path": path.path,
                    "relationships": path.relationships,
                    "confidence": path.confidence,
                    "length": path.path_length
                }
                for path in result.reasoning_paths
            ],
            "inferred_relationships": [
                {
                    "source": rel.source,
                    "target": rel.target,
                    "relation": rel.relation_type,
                    "confidence": rel.confidence,
                    "context": rel.context
                }
                for rel in result.inferred_relationships
            ],
            "entity_clusters": result.entity_clusters,
            "explanation": result.explanation,
            "confidence": result.confidence,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in enhanced query processing: {str(e)}")

@app.post("/entity/link")
async def link_entities(entities: List[Dict[str, Any]] = Body(...)):
    """Link similar entities across documents."""
    try:
        # Convert to Entity objects
        entity_objects = []
        for entity_data in entities:
            entity = Entity(
                name=entity_data["name"],
                entity_type=entity_data.get("type", "unknown"),
                description=entity_data.get("description", ""),
                confidence=entity_data.get("confidence", 1.0),
                metadata=entity_data.get("metadata", {})
            )
            entity_objects.append(entity)
        
        # Link entities
        links = entity_linker.link_entities(entity_objects)
        
        return {
            "entities": entities,
            "links": [
                {
                    "source": link.source_entity.name,
                    "target": link.target_entity.name,
                    "similarity_score": link.similarity_score,
                    "link_type": link.link_type,
                    "confidence": link.confidence
                }
                for link in links
            ],
            "clusters": entity_linker.get_entity_clusters(),
            "statistics": entity_linker.get_entity_statistics(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error linking entities: {str(e)}")

@app.post("/entity/disambiguate")
async def disambiguate_entity(
    entity: Dict[str, Any] = Body(...),
    context: str = Body(...)
):
    """Disambiguate an entity based on context."""
    try:
        entity_obj = Entity(
            name=entity["name"],
            entity_type=entity.get("type", "unknown"),
            description=entity.get("description", ""),
            confidence=entity.get("confidence", 1.0),
            metadata=entity.get("metadata", {})
        )
        
        disambiguated = entity_linker.disambiguate_entity(entity_obj, context)
        
        return {
            "original_entity": entity,
            "disambiguated_entity": {
                "name": disambiguated.name,
                "type": disambiguated.entity_type,
                "description": disambiguated.description,
                "confidence": disambiguated.confidence
            },
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disambiguating entity: {str(e)}")

@app.post("/reasoning/explain-relationship")
async def explain_relationship(
    source: str = Body(...),
    target: str = Body(...),
    entities: List[Dict[str, Any]] = Body(...),
    relationships: List[Dict[str, Any]] = Body(...)
):
    """Explain the relationship between two entities using graph reasoning."""
    try:
        # Convert to Entity and Relationship objects
        entity_objects = []
        for entity_data in entities:
            entity = Entity(
                name=entity_data["name"],
                entity_type=entity_data.get("type", "unknown"),
                description=entity_data.get("description", ""),
                confidence=entity_data.get("confidence", 1.0),
                metadata=entity_data.get("metadata", {})
            )
            entity_objects.append(entity)
        
        relationship_objects = []
        for rel_data in relationships:
            rel = Relationship(
                source=rel_data["source"],
                target=rel_data["target"],
                relation_type=rel_data["relation"],
                context=rel_data.get("context", ""),
                confidence=rel_data.get("confidence", 1.0),
                metadata=rel_data.get("metadata", {})
            )
            relationship_objects.append(rel)
        
        # Build graph and explain relationship
        graph_reasoner.build_graph(entity_objects, relationship_objects)
        reasoning_result = graph_reasoner.explain_relationship(source, target)
        
        return {
            "source": source,
            "target": target,
            "paths": [
                {
                    "source": path.source,
                    "target": path.target,
                    "path": path.path,
                    "relationships": path.relationships,
                    "confidence": path.confidence,
                    "length": path.path_length
                }
                for path in reasoning_result.paths
            ],
            "inferred_relationships": [
                {
                    "source": rel.source,
                    "target": rel.target,
                    "relation": rel.relation_type,
                    "confidence": rel.confidence,
                    "context": rel.context
                }
                for rel in reasoning_result.inferred_relationships
            ],
            "explanation": reasoning_result.reasoning_steps,
            "confidence": reasoning_result.confidence,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining relationship: {str(e)}")

@app.post("/reasoning/multi-hop")
async def multi_hop_reasoning(
    source: str = Body(...),
    target: str = Body(...),
    max_hops: int = Body(3),
    entities: List[Dict[str, Any]] = Body(...),
    relationships: List[Dict[str, Any]] = Body(...)
):
    """Perform multi-hop reasoning between entities."""
    try:
        # Convert to Entity and Relationship objects
        entity_objects = []
        for entity_data in entities:
            entity = Entity(
                name=entity_data["name"],
                entity_type=entity_data.get("type", "unknown"),
                description=entity_data.get("description", ""),
                confidence=entity_data.get("confidence", 1.0),
                metadata=entity_data.get("metadata", {})
            )
            entity_objects.append(entity)
        
        relationship_objects = []
        for rel_data in relationships:
            rel = Relationship(
                source=rel_data["source"],
                target=rel_data["target"],
                relation_type=rel_data["relation"],
                context=rel_data.get("context", ""),
                confidence=rel_data.get("confidence", 1.0),
                metadata=rel_data.get("metadata", {})
            )
            relationship_objects.append(rel)
        
        # Build graph and find paths
        graph_reasoner.build_graph(entity_objects, relationship_objects)
        paths = graph_reasoner.find_paths(source, target, max_hops)
        inferred_rels = graph_reasoner.infer_relationships(source, target, max_hops)
        
        return {
            "source": source,
            "target": target,
            "max_hops": max_hops,
            "paths": [
                {
                    "source": path.source,
                    "target": path.target,
                    "path": path.path,
                    "relationships": path.relationships,
                    "confidence": path.confidence,
                    "length": path.path_length
                }
                for path in paths
            ],
            "inferred_relationships": [
                {
                    "source": rel.source,
                    "target": rel.target,
                    "relation": rel.relation_type,
                    "confidence": rel.confidence,
                    "context": rel.context
                }
                for rel in inferred_rels
            ],
            "path_count": len(paths),
            "inferred_count": len(inferred_rels),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in multi-hop reasoning: {str(e)}")

@app.get("/reasoning/graph-statistics")
async def get_graph_statistics():
    """Get statistics about the knowledge graph."""
    try:
        stats = graph_reasoner.get_graph_statistics()
        centrality = graph_reasoner.get_entity_centrality()
        clusters = graph_reasoner.find_entity_clusters()
        
        return {
            "graph_statistics": stats,
            "entity_centrality": centrality,
            "entity_clusters": clusters,
            "cluster_count": len(clusters),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting graph statistics: {str(e)}")

@app.get("/query/statistics")
async def get_query_statistics():
    """Get statistics about query processing."""
    try:
        stats = enhanced_query_processor.get_query_statistics()
        return {
            "query_statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting query statistics: {str(e)}")

@app.post("/api/analyze-query-intent")
async def analyze_query_intent(query: str):
    """Analyze the intent of a user query."""
    try:
        intent = enhanced_query_processor.analyze_query_intent(query)
        return {
            "intent_type": intent.intent_type,
            "confidence": intent.confidence,
            "entities": intent.entities,
            "reasoning_required": intent.reasoning_required,
            "search_strategy": intent.search_strategy,
            "complexity_level": intent.complexity_level,
            "follow_up_questions": intent.follow_up_questions
        }
    except Exception as e:
        logger.error(f"Error analyzing query intent: {e}")
        return {"error": str(e)}

@app.post("/api/advanced-reasoning")
async def advanced_reasoning(query: str):
    """Perform advanced reasoning on a query."""
    try:
        # Extract entities from query
        extraction_result = entity_extractor.extract_entities_and_relations(query)
        entities = [entity.name for entity in extraction_result.entities]
        
        # Execute reasoning
        reasoning_paths = advanced_reasoning_engine.execute_reasoning(query, entities)
        
        # Generate explanation
        explanation = advanced_reasoning_engine.generate_reasoning_explanation(reasoning_paths)
        
        return {
            "query": query,
            "entities": entities,
            "reasoning_paths": [
                {
                    "path_type": path.path_type,
                    "entities": path.entities,
                    "relationships": path.relationships,
                    "confidence": path.confidence,
                    "evidence": path.evidence,
                    "reasoning_chain": path.reasoning_chain
                }
                for path in reasoning_paths
            ],
            "explanation": explanation,
            "total_paths": len(reasoning_paths)
        }
    except Exception as e:
        logger.error(f"Error in advanced reasoning: {e}")
        return {"error": str(e)}

@app.post("/api/enhanced-query")
async def enhanced_query(query: str, context: Optional[Dict] = None):
    """Process a query with enhanced capabilities including reasoning and intent analysis."""
    try:
        result = enhanced_query_processor.process_enhanced_query(query, context)
        
        return {
            "query": query,
            "answer": result.answer,
            "sources": result.sources,
            "reasoning_paths": [
                {
                    "path_type": path.path_type,
                    "entities": path.entities,
                    "relationships": path.relationships,
                    "confidence": path.confidence,
                    "evidence": path.evidence,
                    "reasoning_chain": path.reasoning_chain
                }
                for path in result.reasoning_paths
            ],
            "confidence": result.confidence,
            "search_strategy": {
                "components": result.search_strategy.components,
                "confidence": result.search_strategy.confidence,
                "explanation": result.search_strategy.explanation
            },
            "follow_up_suggestions": result.follow_up_suggestions,
            "explanation": result.explanation
        }
    except Exception as e:
        logger.error(f"Error in enhanced query processing: {e}")
        return {"error": str(e)}

@app.post("/api/query-complexity-analysis")
async def analyze_query_complexity(query: str):
    """Analyze the complexity of a query and determine reasoning requirements."""
    try:
        complexity = advanced_reasoning_engine.analyze_query_complexity(query)
        
        return {
            "query": query,
            "primary_reasoning": complexity['primary_reasoning'],
            "detected_patterns": complexity['detected_patterns'],
            "complexity_level": complexity['complexity_level'],
            "requires_multi_hop": complexity['requires_multi_hop']
        }
    except Exception as e:
        logger.error(f"Error analyzing query complexity: {e}")
        return {"error": str(e)}

@app.post("/api/causal-reasoning")
async def causal_reasoning(query: str):
    """Perform causal reasoning to find cause-effect relationships."""
    try:
        # Extract entities from query
        extraction_result = entity_extractor.extract_entities_and_relations(query)
        entities = [entity.name for entity in extraction_result.entities]
        
        # Execute causal reasoning
        reasoning_paths = advanced_reasoning_engine.causal_reasoning(query, entities)
        
        return {
            "query": query,
            "entities": entities,
            "causal_chains": [
                {
                    "path_type": path.path_type,
                    "entities": path.entities,
                    "relationships": path.relationships,
                    "confidence": path.confidence,
                    "evidence": path.evidence,
                    "reasoning_chain": path.reasoning_chain
                }
                for path in reasoning_paths
            ],
            "total_chains": len(reasoning_paths)
        }
    except Exception as e:
        logger.error(f"Error in causal reasoning: {e}")
        return {"error": str(e)}

@app.post("/api/comparative-reasoning")
async def comparative_reasoning(query: str):
    """Perform comparative reasoning between entities."""
    try:
        # Extract entities from query
        extraction_result = entity_extractor.extract_entities_and_relations(query)
        entities = [entity.name for entity in extraction_result.entities]
        
        # Execute comparative reasoning
        reasoning_paths = advanced_reasoning_engine.comparative_reasoning(query, entities)
        
        return {
            "query": query,
            "entities": entities,
            "comparisons": [
                {
                    "path_type": path.path_type,
                    "entities": path.entities,
                    "relationships": path.relationships,
                    "confidence": path.confidence,
                    "evidence": path.evidence,
                    "reasoning_chain": path.reasoning_chain
                }
                for path in reasoning_paths
            ],
            "total_comparisons": len(reasoning_paths)
        }
    except Exception as e:
        logger.error(f"Error in comparative reasoning: {e}")
        return {"error": str(e)}

@app.post("/api/multi-hop-reasoning")
async def multi_hop_reasoning(query: str, max_hops: int = 3):
    """Perform multi-hop reasoning across the knowledge graph."""
    try:
        # Extract entities from query
        extraction_result = entity_extractor.extract_entities_and_relations(query)
        entities = [entity.name for entity in extraction_result.entities]
        
        # Execute multi-hop reasoning
        reasoning_paths = advanced_reasoning_engine.multi_hop_reasoning(query, entities)
        
        return {
            "query": query,
            "entities": entities,
            "max_hops": max_hops,
            "reasoning_paths": [
                {
                    "path_type": path.path_type,
                    "entities": path.entities,
                    "relationships": path.relationships,
                    "confidence": path.confidence,
                    "evidence": path.evidence,
                    "reasoning_chain": path.reasoning_chain
                }
                for path in reasoning_paths
            ],
            "total_paths": len(reasoning_paths)
        }
    except Exception as e:
        logger.error(f"Error in multi-hop reasoning: {e}")
        return {"error": str(e)}

@app.post("/extract-entities-relations-enhanced")
async def extract_entities_relations_enhanced(
    text: str = Form(...),
    domain: str = Form("general"),
    use_spanbert: bool = Form(True),
    use_dependency: bool = Form(True),
    use_entity_linking: bool = Form(True)
):
    """
    Enhanced entity and relationship extraction using multiple methods.
    
    Args:
        text: Text to process
        domain: Domain context
        use_spanbert: Whether to use SpanBERT extraction
        use_dependency: Whether to use dependency parsing
        use_entity_linking: Whether to use entity linking
    """
    try:
        # Get enhanced extractor
        enhanced_extractor = get_enhanced_entity_extractor()
        
        # Configure extraction methods
        enhanced_extractor.use_spanbert = use_spanbert
        enhanced_extractor.use_dependency = use_dependency
        enhanced_extractor.use_entity_linking = use_entity_linking
        
        # Extract entities and relationships
        result = enhanced_extractor.extract_entities_and_relations(text, domain)
        
        # Convert to response format
        entities_response = []
        for entity in result.entities:
            entities_response.append({
                "name": entity.name,
                "type": entity.entity_type,
                "description": entity.description,
                "confidence": entity.confidence,
                "metadata": entity.metadata
            })
        
        relationships_response = []
        for rel in result.relationships:
            relationships_response.append({
                "source": rel.source,
                "target": rel.target,
                "relation_type": rel.relation_type,
                "context": rel.context,
                "confidence": rel.confidence,
                "metadata": rel.metadata
            })
        
        return {
            "text": text,
            "domain": domain,
            "entities": entities_response,
            "relationships": relationships_response,
            "claims": result.claims,
            "entity_count": len(result.entities),
            "relationship_count": len(result.relationships),
            "extraction_method": "enhanced",
            "extraction_metadata": result.extraction_metadata,
            "span_extractions": result.span_extractions,
            "dependency_extractions": result.dependency_extractions,
            "linked_entities": result.linked_entities
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced extraction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/extraction-stats")
async def get_extraction_stats():
    """Get statistics about available extraction methods."""
    try:
        enhanced_extractor = get_enhanced_entity_extractor()
        stats = enhanced_extractor.get_extraction_stats()
        
        return {
            "enhanced_extraction_stats": stats,
            "available_methods": stats["extraction_methods"],
            "spanbert_available": stats["spanbert_available"],
            "dependency_available": stats["dependency_available"],
            "entity_linking_available": stats["entity_linking_available"]
        }
        
    except Exception as e:
        logger.error(f"Error getting extraction stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-enhanced-extraction")
async def test_enhanced_extraction(
    text: str = Form(...),
    domain: str = Form("general")
):
    """Test the enhanced extraction with a sample text."""
    try:
        enhanced_extractor = get_enhanced_entity_extractor()
        
        # Test with all methods enabled
        result = enhanced_extractor.extract_entities_and_relations(text, domain)
        
        return {
            "success": True,
            "message": "Enhanced extraction test completed",
            "entities_found": len(result.entities),
            "relationships_found": len(result.relationships),
            "extraction_methods_used": result.extraction_metadata.get("extraction_methods", []),
            "sample_entities": [
                {
                    "name": entity.name,
                    "type": entity.entity_type,
                    "confidence": entity.confidence,
                    "extraction_method": entity.metadata.get("extraction_method", "unknown")
                }
                for entity in result.entities[:5]  # Show first 5 entities
            ],
            "sample_relationships": [
                {
                    "source": rel.source,
                    "target": rel.target,
                    "relation_type": rel.relation_type,
                    "confidence": rel.confidence,
                    "extraction_method": rel.metadata.get("extraction_method", "unknown")
                }
                for rel in result.relationships[:5]  # Show first 5 relationships
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in enhanced extraction test: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Enhanced extraction test failed"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 