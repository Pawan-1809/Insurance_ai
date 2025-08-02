from fastapi import FastAPI
from app.api import hackrx

app = FastAPI(title="LLM-Powered Intelligent Query-Retrieval System")

app.include_router(hackrx.router)
