import os
import tempfile
import requests
from typing import List, Tuple
import logging
from app.services.pdf_parser import extract_text_from_pdf
from app.services.docx_parser import extract_text_from_docx
from app.services.email_parser import extract_text_from_email
from app.core.config import MAX_CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

def download_file(url: str) -> str:
    """Download file from URL to a temp file and return the path."""
    import urllib.parse
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Remove query params and fragments for filename
        parsed = urllib.parse.urlparse(url)
        base = os.path.basename(parsed.path)
        suffix = os.path.splitext(base)[-1] if '.' in base else ''
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)
            logger.info(f"Downloaded file from {url} to {tmp.name}")
            return tmp.name
    except Exception as e:
        logger.error(f"Failed to download file from {url}: {e}")
        raise RuntimeError(f"Failed to download file: {e}")

def detect_file_type(file_path: str) -> str:
    """Detect file type based on extension."""
    ext = os.path.splitext(file_path)[-1].lower()
    if ext in ['.pdf']:
        return 'pdf'
    elif ext in ['.docx', '.doc']:
        return 'docx'
    elif ext in ['.eml', '.email', '.txt']:
        return 'email'
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def chunk_text(text: str, max_chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Split text into overlapping chunks for better semantic search.
    
    Args:
        text: Text to chunk
        max_chunk_size: Maximum size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    max_chunk_size = max_chunk_size or MAX_CHUNK_SIZE
    overlap = overlap or CHUNK_OVERLAP
    
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chunk_size
        
        # Try to break at sentence boundaries
        if end < len(text):
            # Look for sentence endings
            for i in range(end, max(start + max_chunk_size // 2, end - 100), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        if start >= len(text):
            break
    
    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks

def parse_document(file_path: str) -> List[str]:
    """Parse document and return text chunks."""
    file_type = detect_file_type(file_path)
    
    try:
        if file_type == 'pdf':
            text = extract_text_from_pdf(file_path)
        elif file_type == 'docx':
            text = extract_text_from_docx(file_path)
        elif file_type == 'email':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_email = f.read()
            text = extract_text_from_email(raw_email)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Clean and chunk the text
        text = text.strip()
        if not text:
            logger.warning(f"Extracted text is empty from {file_path}")
            return []
        
        chunks = chunk_text(text)
        logger.info(f"Parsed {file_type} document into {len(chunks)} chunks")
        return chunks
        
    except Exception as e:
        logger.error(f"Failed to parse document {file_path}: {e}")
        raise RuntimeError(f"Document parsing failed: {e}")

def ingest_document(source: str, is_url: bool = True) -> Tuple[List[str], str]:
    """
    Download and parse a document from a URL or local path.
    
    Args:
        source: URL or file path
        is_url: Whether source is a URL
        
    Returns:
        Tuple of (chunks, file_path)
    """
    try:
        if is_url:
            file_path = download_file(source)
        else:
            file_path = source
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
        
        chunks = parse_document(file_path)
        
        if not chunks:
            raise RuntimeError("No text content extracted from document")
        
        logger.info(f"Successfully ingested document: {len(chunks)} chunks")
        return chunks, file_path
        
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        raise RuntimeError(f"Document ingestion failed: {e}")
