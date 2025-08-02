# LLM-Powered Intelligent Query-Retrieval System

An intelligent system for processing documents and answering questions using FAISS vector search and GPT-4. This system is designed for insurance, legal, HR, and compliance domains.

## Features

- **Document Processing**: Supports PDF, DOCX, and email documents
- **Semantic Search**: Uses FAISS for efficient vector similarity search
- **LLM Integration**: Powered by OpenAI GPT-4 for intelligent question answering
- **Structured Responses**: Returns JSON responses with explainable rationale
- **Authentication**: Bearer token-based API security
- **Database Storage**: PostgreSQL/SQLite support for tracking documents and queries

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Document      │    │   FAISS Vector  │
│                 │    │   Processing    │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   OpenAI GPT-4  │    │   PostgreSQL    │    │   Document      │
│   LLM Client    │    │   Database      │    │   Parsers       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **LLM**: OpenAI GPT-4
- **Embeddings**: OpenAI text-embedding-ada-002
- **Database**: PostgreSQL (with SQLite fallback)
- **Document Processing**: pdfplumber, python-docx

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Insurance_ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -m app.db.init_db
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
POSTGRES_URL=postgresql://username:password@localhost:5432/hackrx_db
# For SQLite: POSTGRES_URL=sqlite:///./hackrx.db

# FAISS Configuration
FAISS_INDEX_PATH=faiss_index
FAISS_DIMENSION=1536

# HackRX Token
HACKRX_TOKEN=d1b791fa0ef5092d9cd051b2b09df2473d1e2ea07e09fe6c61abb5722dfbc7d3

# Logging
LOG_LEVEL=INFO

# Document Processing
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# LLM Configuration
LLM_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-ada-002
```

## Usage

### Starting the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Main Query Endpoint
```bash
POST /hackrx/run
Content-Type: application/json
Authorization: Bearer d1b791fa0ef5092d9cd051b2b09df2473d1e2ea07e09fe6c61abb5722dfbc7d3

{
  "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
  "questions": [
    "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?"
  ]
}
```

### Sample Response

```json
{
  "answers": [
    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
  ]
}
```

## Project Structure

```
Insurance_ai/
├── app/
│   ├── api/
│   │   └── hackrx.py          # API endpoints
│   ├── core/
│   │   └── config.py          # Configuration management
│   ├── db/
│   │   ├── database.py        # Database models and connection
│   │   └── init_db.py         # Database initialization
│   ├── models/
│   │   ├── request.py         # Request models
│   │   └── response.py        # Response models
│   ├── services/
│   │   ├── document_ingestion.py  # Document processing
│   │   ├── embedding_pipeline.py  # FAISS operations
│   │   ├── faiss_client.py        # FAISS client
│   │   ├── llm_client.py          # OpenAI integration
│   │   ├── pdf_parser.py          # PDF text extraction
│   │   ├── docx_parser.py         # DOCX text extraction
│   │   ├── email_parser.py        # Email text extraction
│   │   ├── pipeline.py            # Main processing pipeline
│   │   └── scoring.py             # Scoring logic
│   └── main.py                # FastAPI application
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables template
├── README.md                 # This file
└── Dockerfile               # Docker configuration
```

## Development

### Running Tests
```bash
# Add test files and run
python -m pytest tests/
```

### Code Quality
```bash
# Format code
black app/
# Lint code
flake8 app/
```

## Docker Deployment

```bash
# Build image
docker build -t hackrx-system .

# Run container
docker run -p 8000:8000 --env-file .env hackrx-system
```

## Performance Considerations

- **FAISS Index**: Uses in-memory FAISS with disk persistence
- **Chunking**: Configurable chunk size and overlap for optimal retrieval
- **Caching**: FAISS index persists between requests
- **Error Handling**: Comprehensive error handling and logging

## Security

- Bearer token authentication
- Input validation with Pydantic
- Secure file handling
- Environment variable configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is developed for the HackRX hackathon.

## Support

For issues and questions, please refer to the project documentation or create an issue in the repository.
