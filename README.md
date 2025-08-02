# LLM-Powered Intelligent Query-Retrieval System

## Overview

A backend system for contextual query answering over insurance, legal, HR, and compliance documents using LLMs, Pinecone, and FastAPI.

## Setup

1. `python -m venv venv`
2. `venv\Scripts\activate` (Windows)
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your API keys
5. `uvicorn app.main:app --reload`

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
