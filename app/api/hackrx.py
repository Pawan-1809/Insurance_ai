
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.request import HackrxRequest
from app.models.response import HackrxResponse
from app.services.pipeline import process_query_pipeline
from app.core.config import HACKRX_TOKEN
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "LLM-Powered Intelligent Query-Retrieval System is running"}

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the Bearer token for authentication."""
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    if credentials.credentials != HACKRX_TOKEN:
        logger.warning(f"Unauthorized access attempt with token: {credentials.credentials[:10]}...")
        raise HTTPException(status_code=403, detail="Unauthorized")

@router.post("/hackrx/run", response_model=HackrxResponse)
async def run_hackrx(request: HackrxRequest, auth: HTTPAuthorizationCredentials = Depends(verify_token)):
    """
    Main endpoint for document upload and question answering.
    
    Args:
        request: HackrxRequest containing documents and questions
        auth: Authentication credentials
        
    Returns:
        HackrxResponse with answers for all questions
    """
    try:
        logger.info(f"Processing request with {len(request.questions)} questions")
        result = await process_query_pipeline(request)
        logger.info(f"Successfully processed request, returning {len(result.answers)} answers")
        return result
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
