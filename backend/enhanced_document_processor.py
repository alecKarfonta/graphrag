from typing import List, Dict, Any, Optional
from document_processor import DocumentProcessor, DocumentChunk, DocumentMetadata
from semantic_chunker import SemanticChunker
import spacy
import re
from datetime import datetime

class EnhancedDocumentProcessor:
    """Enhanced document processor with semantic chunking and metadata extraction."""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.semantic_chunker = SemanticChunker()
        # Load spaCy model for NLP tasks
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if model not installed
            self.nlp = None
    
    def process_document_enhanced(self, file_path: str, use_semantic_chunking: bool = True) -> List[DocumentChunk]:
        """Process document with enhanced features."""
        # Get basic chunks from document processor
        basic_chunks = self.document_processor.process_document(file_path)
        
        if not use_semantic_chunking:
            return basic_chunks
        
        # Apply semantic chunking to each basic chunk
        enhanced_chunks = []
        for chunk in basic_chunks:
            # Determine content type for adaptive chunking
            content_type = self._classify_content_type(chunk.text)
            
            # Create semantic chunks
            semantic_chunks = self.semantic_chunker.create_adaptive_chunks(
                chunk.text, content_type
            )
            
            # Create enhanced chunks with semantic boundaries
            for i, semantic_chunk in enumerate(semantic_chunks):
                enhanced_chunk = DocumentChunk(
                    text=semantic_chunk,
                    chunk_id=f"{chunk.chunk_id}_semantic_{i}",
                    source_file=chunk.source_file,
                    page_number=chunk.page_number,
                    section_header=chunk.section_header,
                    chunk_index=chunk.chunk_index,
                    metadata=self._enhance_metadata(chunk.metadata, semantic_chunk)
                )
                enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks
    
    def extract_enhanced_metadata(self, file_path: str) -> DocumentMetadata:
        """Extract enhanced metadata including content analysis."""
        metadata = self.document_processor.extract_metadata(file_path)
        
        # Read file content for analysis
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Extract additional metadata
        metadata.sections = self._extract_sections(content)
        metadata.creation_date = self._extract_creation_date(content)
        metadata.author = self._extract_author(content)
        
        return metadata
    
    def _classify_content_type(self, text: str) -> str:
        """Classify content type for adaptive chunking."""
        if not text:
            return "general"
        
        # Simple heuristics for content classification
        text_lower = text.lower()
        
        # Technical content indicators
        technical_indicators = [
            'specification', 'technical', 'procedure', 'installation',
            'configuration', 'api', 'function', 'parameter', 'error',
            'warning', 'debug', 'log', 'system', 'component'
        ]
        
        # Narrative content indicators
        narrative_indicators = [
            'story', 'narrative', 'description', 'background',
            'history', 'overview', 'introduction', 'conclusion'
        ]
        
        # Structured content indicators
        structured_indicators = [
            'table', 'list', 'item', 'step', 'instruction',
            'checklist', 'form', 'data', 'record'
        ]
        
        # Count matches
        technical_count = sum(1 for indicator in technical_indicators if indicator in text_lower)
        narrative_count = sum(1 for indicator in narrative_indicators if indicator in text_lower)
        structured_count = sum(1 for indicator in structured_indicators if indicator in text_lower)
        
        # Determine content type
        if technical_count > narrative_count and technical_count > structured_count:
            return "technical"
        elif narrative_count > technical_count and narrative_count > structured_count:
            return "narrative"
        elif structured_count > technical_count and structured_count > narrative_count:
            return "structured"
        else:
            return "general"
    
    def _enhance_metadata(self, base_metadata: Dict[str, Any], chunk_text: str) -> Dict[str, Any]:
        """Enhance metadata with chunk-specific information."""
        enhanced_metadata = base_metadata.copy() if base_metadata else {}
        
        # Add chunk-specific metadata
        enhanced_metadata.update({
            'word_count': len(chunk_text.split()),
            'character_count': len(chunk_text),
            'content_type': self._classify_content_type(chunk_text),
            'has_numbers': bool(re.search(r'\d', chunk_text)),
            'has_urls': bool(re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', chunk_text)),
            'sentence_count': len(re.split(r'[.!?]+', chunk_text))
        })
        
        return enhanced_metadata
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from content."""
        sections = []
        
        # Look for common section patterns
        section_patterns = [
            r'^#+\s+(.+)$',  # Markdown headers
            r'^[A-Z][A-Z\s]+\n[-=]+\n',  # Underlined headers
            r'^\d+\.\s+(.+)$',  # Numbered sections
            r'^[A-Z][^.!?]*[.!?]?\n',  # Capitalized lines
        ]
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section patterns
            for pattern in section_patterns:
                if re.match(pattern, line, re.MULTILINE):
                    # Clean up the section title
                    title = re.sub(r'^#+\s+', '', line)
                    title = re.sub(r'^\d+\.\s+', '', title)
                    if title and len(title) < 100:  # Reasonable length
                        sections.append(title)
                    break
        
        return sections[:10]  # Limit to first 10 sections
    
    def _extract_creation_date(self, content: str) -> Optional[str]:
        """Extract creation date from content."""
        # Look for date patterns
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_author(self, content: str) -> Optional[str]:
        """Extract author information from content."""
        # Look for author patterns
        author_patterns = [
            r'Author[:\s]+([^\n]+)',
            r'By[:\s]+([^\n]+)',
            r'Written by[:\s]+([^\n]+)',
            r'©\s*\d{4}\s+([^\n]+)',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                author = match.group(1).strip()
                if len(author) < 100:  # Reasonable length
                    return author
        
        return None
    
    def process_batch(self, file_paths: List[str], use_semantic_chunking: bool = True) -> Dict[str, List[DocumentChunk]]:
        """Process multiple documents in batch."""
        results = {}
        
        for file_path in file_paths:
            try:
                chunks = self.process_document_enhanced(file_path, use_semantic_chunking)
                results[file_path] = chunks
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                results[file_path] = []
        
        return results 