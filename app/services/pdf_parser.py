# PDF parsing utility
import pdfplumber
from typing import List

# TODO: Add error handling, chunking, and metadata extraction

def extract_text_from_pdf(file_path: str) -> List[str]:
    text_chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_chunks.append(text)
    return text_chunks
