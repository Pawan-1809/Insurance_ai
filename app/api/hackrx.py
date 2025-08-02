from fastapi import APIRouter, HTTPException, Request, status, Depends
from app.models.request import HackrxRequest
from app.models.response import HackrxResponse
from app.services.pipeline import process_query_pipeline

router = APIRouter()

@router.post("/hackrx/run", response_model=HackrxResponse)
async def run_hackrx(request: HackrxRequest):
    """
    Main endpoint for document upload and question answering.
    """
    try:
        result = await process_query_pipeline(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
