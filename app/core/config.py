import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is required. Please set it in your .env file.")

# Database Configuration
POSTGRES_URL = os.getenv("POSTGRES_URL", "sqlite:///./hackrx.db")
if not POSTGRES_URL:
    # Fallback to SQLite for development
    POSTGRES_URL = "sqlite:///./hackrx.db"

# FAISS Configuration
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")
FAISS_DIMENSION = int(os.getenv("FAISS_DIMENSION", "1536"))  # text-embedding-3-small uses 1536 dimensions

# HackRX Token
HACKRX_TOKEN = os.getenv("HACKRX_TOKEN", "d1b791fa0ef5092d9cd051b2b09df2473d1e2ea07e09fe6c61abb5722dfbc7d3")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Document Processing Configuration
MAX_CHUNK_SIZE = int(os.getenv("MAX_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")  # Changed to gpt-3.5-turbo
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")  # Updated to newer model
