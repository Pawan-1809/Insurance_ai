# LLM-Powered Intelligent Query-Retrieval System

## Overview

A backend system for contextual query answering over insurance, legal, HR, and compliance documents using LLMs, Pinecone, and FastAPI.

## Setup

1. `python -m venv venv`
2. `venv\Scripts\activate` (Windows)
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your API keys and tokens
5. `uvicorn app.main:app --reload`

## Deployment (Railway/Render)

- Use the provided Dockerfile for containerized deployment.
- Set all environment variables from `.env.example` in your platform's dashboard.
- Expose port 8000.
- Health check endpoint: `/health`

## API

- **POST /hackrx/run**
  - Accepts: JSON with `documents` (URL or file), `questions` (list)
  - Returns: JSON with answers, rationale, and clause references

## Structure

- `app/` - Main backend code
- `tests/` - Unit/integration tests

## TODO

- Implement PDF/DOC/email parsing (uses Python's built-in `email` module, no extra install needed)
- Integrate Pinecone and OpenAI
- Add scoring logic
- Add authentication
