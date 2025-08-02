# Email parsing utility
from email import message_from_string
from typing import List

# TODO: Add support for .eml files and attachments

def extract_text_from_email(raw_email: str) -> List[str]:
    msg = message_from_string(raw_email)
    body = []
    def decode_payload(payload):
        if isinstance(payload, bytes):
            return payload.decode(errors="ignore")
        return payload or ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                body.append(decode_payload(payload))
    else:
        payload = msg.get_payload(decode=True)
        body.append(decode_payload(payload))
    return body
