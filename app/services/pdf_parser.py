# PDF parsing utility
import pdfplumber
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text as a single string
    """
    try:
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(text.strip())
                    logger.debug(f"Extracted text from page {page_num + 1}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
        
        full_text = "\n\n".join(text_parts)
        logger.info(f"Successfully extracted {len(text_parts)} pages from PDF")
        return full_text
        
    except Exception as e:
        logger.error(f"Failed to extract text from PDF {file_path}: {e}")
        raise RuntimeError(f"PDF text extraction failed: {e}")
