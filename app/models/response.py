from pydantic import BaseModel
from typing import List, Optional, Dict

class AnswerItem(BaseModel):
    answer: str
    rationale: Optional[str] = None
    clause_reference: Optional[str] = None
    score: Optional[float] = None

class HackrxResponse(BaseModel):
    answers: List[Dict[str, object]]  # List of answer dictionaries with structured format supporting different value types
