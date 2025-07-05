from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import tempfile
import shutil
import json
from document_processor import DocumentProcessor, DocumentChunk
from enhanced_document_processor import EnhancedDocumentProcessor
from hybrid_retriever import HybridRetriever
from query_processor import QueryProcessor
from entity_extractor import EntityExtractor
from knowledge_graph_builder import KnowledgeGraphBuilder
from datetime import datetime

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
async def advanced_search(
    query: str,
    search_type: str = "hybrid",  # "vector", "graph", "keyword", "hybrid"
    top_k: int = 10
):
    """Advanced search with different search strategies."""
    try:
        # Process query
        query_analysis = query_processor.get_query_analysis(query)
        
        # Perform search based on type
        if search_type == "vector":
            results = hybrid_retriever.vector_search(query, top_k=top_k)
        elif search_type == "graph":
            results = hybrid_retriever.graph_search(query, top_k=top_k)
        elif search_type == "keyword":
            results = hybrid_retriever.keyword_search(query, top_k=top_k)
        else:  # hybrid
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
        
        return {
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
async def get_knowledge_graph_stats():
    """Get knowledge graph statistics."""
    try:
        if not knowledge_graph_builder:
            raise HTTPException(status_code=503, detail="Knowledge graph not available")
        
        stats = knowledge_graph_builder.get_graph_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting graph stats: {str(e)}")

@app.get("/knowledge-graph/export")
async def export_knowledge_graph(format: str = "json"):
    """Export knowledge graph data."""
    try:
        if not knowledge_graph_builder:
            raise HTTPException(status_code=503, detail="Knowledge graph not available")
        
        if format == "json":
            graph_data = knowledge_graph_builder.export_graph_json()
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 