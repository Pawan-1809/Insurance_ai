# Email parsing utility
from email import message_from_string
import logging

logger = logging.getLogger(__name__)

def extract_text_from_email(raw_email: str) -> str:
    """
    Extract text from email content.
    
    Args:
        raw_email: Raw email content as string
        
    Returns:
        Extracted text as a single string
    """
    try:
        msg = message_from_string(raw_email)
        body_parts = []
        
        def decode_payload(payload):
            if isinstance(payload, bytes):
                return payload.decode(errors="ignore")
            return payload or ""
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    text = decode_payload(payload)
                    if text.strip():
                        body_parts.append(text.strip())
        else:
            payload = msg.get_payload(decode=True)
            text = decode_payload(payload)
            if text.strip():
                body_parts.append(text.strip())
        
        full_text = "\n\n".join(body_parts)
        logger.info(f"Successfully extracted text from email with {len(body_parts)} parts")
        return full_text
        
    except Exception as e:
        logger.error(f"Failed to extract text from email: {e}")
        raise RuntimeError(f"Email text extraction failed: {e}")
