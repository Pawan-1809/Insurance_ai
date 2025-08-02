# DOCX parsing utility
from docx import Document
import logging

logger = logging.getLogger(__name__)

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from DOCX file.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Extracted text as a single string
    """
    try:
        doc = Document(file_path)
        text_parts = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text.strip())
        
        full_text = "\n\n".join(text_parts)
        logger.info(f"Successfully extracted text from DOCX with {len(text_parts)} paragraphs")
        return full_text
        
    except Exception as e:
        logger.error(f"Failed to extract text from DOCX {file_path}: {e}")
        raise RuntimeError(f"DOCX text extraction failed: {e}")
