
from fastapi import APIRouter, HTTPException, Request, status, Depends, Header
from app.models.request import HackrxRequest
from app.models.response import HackrxResponse
from app.services.pipeline import process_query_pipeline
import os

HACKRX_TOKEN = os.getenv("HACKRX_TOKEN", "d1b791fa0ef5092d9cd051b2b09df2473d1e2ea07e09fe6c61abb5722dfbc7d3")


router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

def verify_token(authorization: str = Header(...)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    token = authorization.split(" ", 1)[1]
    if token != HACKRX_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")

@router.post("/hackrx/run", response_model=HackrxResponse)
async def run_hackrx(request: HackrxRequest, auth: str = Depends(verify_token)):
    """
    Main endpoint for document upload and question answering.
    """
    try:
        result = await process_query_pipeline(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
