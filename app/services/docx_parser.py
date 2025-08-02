# DOCX parsing utility
from docx import Document
from typing import List

# TODO: Add error handling, chunking, and metadata extraction

def extract_text_from_docx(file_path: str) -> List[str]:
    doc = Document(file_path)
    return [para.text for para in doc.paragraphs if para.text.strip()]
