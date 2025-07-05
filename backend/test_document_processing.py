#!/usr/bin/env python3
"""Test script for document processing functionality."""

import os
import tempfile
from document_processor import DocumentProcessor
from enhanced_document_processor import EnhancedDocumentProcessor

def create_test_files():
    """Create test files for different formats."""
    test_files = {}
    
    # Test text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""This is a test document.
        
        Section 1: Introduction
        This is the introduction section with some technical content.
        The system processes documents using advanced algorithms.
        
        Section 2: Technical Details
        The document processor supports multiple formats including PDF, DOCX, and TXT.
        It uses semantic chunking for better content organization.
        
        Section 3: Conclusion
        This concludes our test document with various content types.
        """)
        test_files['txt'] = f.name
    
    # Test HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write("""<!DOCTYPE html>
        <html>
        <head><title>Test Document</title></head>
        <body>
        <h1>Test HTML Document</h1>
        <p>This is a paragraph with some content.</p>
        <h2>Technical Section</h2>
        <p>This section contains technical information about the system.</p>
        </body>
        </html>
        """)
        test_files['html'] = f.name
    
    # Test CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("""Name,Age,Department
        John Doe,30,Engineering
        Jane Smith,25,Marketing
        Bob Johnson,35,Sales
        """)
        test_files['csv'] = f.name
    
    return test_files

def test_basic_processing():
    """Test basic document processing."""
    print("Testing basic document processing...")
    
    processor = DocumentProcessor()
    test_files = create_test_files()
    
    for file_type, file_path in test_files.items():
        print(f"\nProcessing {file_type} file: {file_path}")
        try:
            chunks = processor.process_document(file_path)
            print(f"  - Created {len(chunks)} chunks")
            for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                print(f"  - Chunk {i+1}: {len(chunk.text)} chars, ID: {chunk.chunk_id}")
        except Exception as e:
            print(f"  - Error: {e}")
    
    # Clean up test files
    for file_path in test_files.values():
        try:
            os.unlink(file_path)
        except:
            pass

def test_enhanced_processing():
    """Test enhanced document processing with semantic chunking."""
    print("\nTesting enhanced document processing...")
    
    processor = EnhancedDocumentProcessor()
    test_files = create_test_files()
    
    for file_type, file_path in test_files.items():
        print(f"\nProcessing {file_type} file with semantic chunking: {file_path}")
        try:
            chunks = processor.process_document_enhanced(file_path, use_semantic_chunking=True)
            print(f"  - Created {len(chunks)} semantic chunks")
            for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                print(f"  - Chunk {i+1}: {len(chunk.text)} chars, ID: {chunk.chunk_id}")
                if chunk.metadata:
                    content_type = chunk.metadata.get('content_type', 'unknown')
                    print(f"    Content type: {content_type}")
        except Exception as e:
            print(f"  - Error: {e}")
    
    # Clean up test files
    for file_path in test_files.values():
        try:
            os.unlink(file_path)
        except:
            pass

def test_metadata_extraction():
    """Test metadata extraction."""
    print("\nTesting metadata extraction...")
    
    processor = EnhancedDocumentProcessor()
    test_files = create_test_files()
    
    for file_type, file_path in test_files.items():
        print(f"\nExtracting metadata from {file_type} file: {file_path}")
        try:
            metadata = processor.extract_enhanced_metadata(file_path)
            print(f"  - Title: {metadata.title}")
            print(f"  - File type: {metadata.file_type}")
            print(f"  - File size: {metadata.file_size}")
            if metadata.sections:
                print(f"  - Sections: {metadata.sections[:3]}")  # Show first 3 sections
        except Exception as e:
            print(f"  - Error: {e}")
    
    # Clean up test files
    for file_path in test_files.values():
        try:
            os.unlink(file_path)
        except:
            pass

if __name__ == "__main__":
    print("=== Document Processing Test Suite ===\n")
    
    test_basic_processing()
    test_enhanced_processing()
    test_metadata_extraction()
    
    print("\n=== Test Suite Complete ===") 