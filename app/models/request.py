from pydantic import BaseModel, HttpUrl
from typing import List

class HackrxRequest(BaseModel):
    documents: str  # URL or file path
    questions: List[str]
