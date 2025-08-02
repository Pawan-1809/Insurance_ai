import os
import tempfile
import requests
from typing import List, Tuple
from app.services.pdf_parser import extract_text_from_pdf
from app.services.docx_parser import extract_text_from_docx
from app.services.email_parser import extract_text_from_email

def download_file(url: str) -> str:
    """Download file from URL to a temp file and return the path."""
    response = requests.get(url, stream=True)
    response.raise_for_status()
    suffix = os.path.splitext(url)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        for chunk in response.iter_content(chunk_size=8192):
            tmp.write(chunk)
        return tmp.name

def detect_file_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[-1].lower()
    if ext in ['.pdf']:
        return 'pdf'
    elif ext in ['.docx']:
        return 'docx'
    elif ext in ['.eml', '.email']:
        return 'email'
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def parse_document(file_path: str) -> List[str]:
    file_type = detect_file_type(file_path)
    if file_type == 'pdf':
        return extract_text_from_pdf(file_path)
    elif file_type == 'docx':
        return extract_text_from_docx(file_path)
    elif file_type == 'email':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw_email = f.read()
        return extract_text_from_email(raw_email)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def ingest_document(source: str, is_url: bool = True) -> Tuple[List[str], str]:
    """
    Download and parse a document from a URL or local path.
    Returns (chunks, file_path)
    """
    if is_url:
        file_path = download_file(source)
    else:
        file_path = source
    chunks = parse_document(file_path)
    return chunks, file_path
