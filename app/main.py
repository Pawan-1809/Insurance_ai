from fastapi import FastAPI
from app.api import hackrx
from app.db.init_db import init_database
import logging
from app.core.config import LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="LLM-Powered Intelligent Query-Retrieval System",
    description="An intelligent system for processing documents and answering questions using FAISS vector search and GPT-4",
    version="1.0.0"
)

# Include routers
app.include_router(hackrx.router)

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    try:
        # Initialize database
        init_database()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "LLM-Powered Intelligent Query-Retrieval System",
        "version": "1.0.0",
        "status": "running"
    }
