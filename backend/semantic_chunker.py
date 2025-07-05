from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import DBSCAN
import re

class SemanticChunker:
    """Intelligent text chunking using semantic similarity."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with a sentence transformer model."""
        self.model = SentenceTransformer(model_name)
        self.min_chunk_size = 100
        self.max_chunk_size = 1000
        self.overlap_size = 100
    
    def create_semantic_chunks(self, text: str) -> List[str]:
        """Create semantic chunks based on content similarity."""
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= 1:
            return [text]
        
        # Get embeddings for all sentences
        embeddings = self.model.encode(sentences)
        
        # Use DBSCAN to cluster similar sentences
        clustering = DBSCAN(eps=0.3, min_samples=2).fit(embeddings)
        
        # Group sentences by cluster
        clusters = {}
        for i, label in enumerate(clustering.labels_):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(sentences[i])
        
        # Create chunks from clusters
        chunks = []
        for cluster_sentences in clusters.values():
            chunk_text = " ".join(cluster_sentences)
            
            # Split large clusters into smaller chunks
            if len(chunk_text) > self.max_chunk_size:
                sub_chunks = self._split_large_chunk(chunk_text)
                chunks.extend(sub_chunks)
            else:
                chunks.append(chunk_text)
        
        # If no meaningful clusters found, fall back to size-based chunking
        if not chunks:
            chunks = self._fallback_chunking(text)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex."""
        # Simple sentence splitting - can be improved with more sophisticated NLP
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _split_large_chunk(self, chunk_text: str) -> List[str]:
        """Split large chunks into smaller ones while preserving context."""
        chunks = []
        start = 0
        
        while start < len(chunk_text):
            end = start + self.max_chunk_size
            
            # Try to break at sentence boundary
            if end < len(chunk_text):
                # Look for sentence endings
                for i in range(end, max(start, end - 200), -1):
                    if chunk_text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = chunk_text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Overlap for context retention
            start = end - self.overlap_size
            if start >= len(chunk_text):
                break
        
        return chunks
    
    def _fallback_chunking(self, text: str) -> List[str]:
        """Fallback to size-based chunking when semantic clustering fails."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.max_chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                for i in range(end, max(start, end - 200), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk and len(chunk) >= self.min_chunk_size:
                chunks.append(chunk)
            
            # Overlap for context retention
            start = end - self.overlap_size
            if start >= len(text):
                break
        
        return chunks
    
    def create_adaptive_chunks(self, text: str, content_type: str = "general") -> List[str]:
        """Create chunks with size adapted to content type."""
        # Adjust chunk size based on content type
        if content_type == "technical":
            self.max_chunk_size = 800
            self.min_chunk_size = 150
        elif content_type == "narrative":
            self.max_chunk_size = 1200
            self.min_chunk_size = 80
        elif content_type == "structured":
            self.max_chunk_size = 600
            self.min_chunk_size = 200
        else:
            self.max_chunk_size = 1000
            self.min_chunk_size = 100
        
        return self.create_semantic_chunks(text)
    
    def preserve_structure(self, text: str, structure_markers: Dict[str, str]) -> List[Dict[str, Any]]:
        """Create chunks while preserving document structure."""
        chunks = []
        current_section = ""
        current_subsection = ""
        
        # Split by structure markers
        lines = text.split('\n')
        current_chunk = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            if any(marker in line for marker in structure_markers.get('section', [])):
                # Save current chunk
                if current_chunk:
                    chunks.append({
                        'text': current_chunk,
                        'section': current_section,
                        'subsection': current_subsection
                    })
                    current_chunk = ""
                
                current_section = line
                current_subsection = ""
            
            # Check for subsection headers
            elif any(marker in line for marker in structure_markers.get('subsection', [])):
                if current_chunk:
                    chunks.append({
                        'text': current_chunk,
                        'section': current_section,
                        'subsection': current_subsection
                    })
                    current_chunk = ""
                
                current_subsection = line
            
            else:
                current_chunk += line + "\n"
                
                # Create new chunk if getting too large
                if len(current_chunk) > self.max_chunk_size:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'section': current_section,
                        'subsection': current_subsection
                    })
                    current_chunk = ""
        
        # Add remaining chunk
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'section': current_section,
                'subsection': current_subsection
            })
        
        return chunks 