from app.models.request import HackrxRequest
from app.models.response import HackrxResponse, AnswerItem
from app.services.document_ingestion import ingest_document
from app.services.embedding_pipeline import upsert_chunks_to_faiss, query_faiss
from app.services.llm_client import ask_llm
from app.services.scoring import calculate_score

from app.db.database import SessionLocal, Document, Question, Answer

import uuid
import os
import logging

logger = logging.getLogger("pipeline")
logging.basicConfig(level=logging.INFO)

import asyncio

async def process_query_pipeline(request: HackrxRequest) -> HackrxResponse:
    """
    Main pipeline for processing document upload and answering questions.
    Optimized with parallel processing for faster response times.
    
    Args:
        request: HackrxRequest containing documents and questions
        
    Returns:
        HackrxResponse with answers for all questions
    """
    try:
        # 1. Ingest document (download/parse)
        doc_id = str(uuid.uuid4())
        try:
            chunks, file_path = ingest_document(request.documents, is_url=request.documents.startswith("http"))
            logger.info(f"Successfully ingested document with {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            raise RuntimeError(f"Document ingestion failed: {e}")

        # 2. Upsert chunks to FAISS
        try:
            await upsert_chunks_to_faiss(chunks, doc_id)
            logger.info(f"Successfully upserted chunks to FAISS for document {doc_id}")
        except Exception as e:
            logger.error(f"FAISS upsert failed: {e}")
            raise RuntimeError(f"FAISS upsert failed: {e}")

        # 3. Save document to DB
        db = SessionLocal()
        try:
            doc_obj = Document(name=file_path.split(os.sep)[-1], source_url=request.documents)
            db.add(doc_obj)
            db.commit()
            db.refresh(doc_obj)
            logger.info(f"Saved document to database with ID: {doc_obj.id}")
        except Exception as e:
            logger.error(f"DB save document failed: {e}")
            db.rollback()
            raise RuntimeError(f"DB save document failed: {e}")

        # Define async function to process a single question
        async def process_question(i, question):
            try:
                # 4. Save question to DB
                q_obj = Question(document_id=doc_obj.id, question_text=question)
                db.add(q_obj)
                db.commit()
                db.refresh(q_obj)
                logger.info(f"Saved question {i+1}/{len(request.questions)} to database")
            except Exception as e:
                logger.error(f"DB save question failed: {e}")
                db.rollback()
                return {
                    "answer": f"Database error: {str(e)}",
                    "question": question,
                    "score": 0.0
                }

            # 5. Query FAISS for relevant chunks (reduced to 2 for faster processing)
            try:
                matches = await query_faiss(question, top_k=2)
                if matches:
                    # Only use the most relevant chunks to reduce context size
                    context = "\n".join([m.get("metadata", {}).get("text", "") for m in matches])
                    clause_ref = matches[0].get("id") if matches else None
                    logger.info(f"Found {len(matches)} relevant chunks for question {i+1}")
                else:
                    context = ""
                    clause_ref = None
                    logger.warning(f"No relevant chunks found for question {i+1}")
            except Exception as e:
                logger.error(f"FAISS query failed: {e}")
                context = ""
                clause_ref = None

            # 6. Use LLM to answer with rationale
            try:
                prompt = f"""Answer this question concisely based on the context provided.

Context: {context}

Question: {question}

Provide a direct answer followed by brief reasoning. Be concise.

Answer:"""
                
                llm_response = ask_llm(prompt)
                
                # Extract answer and rationale from LLM response
                if "Answer:" in llm_response:
                    parts = llm_response.split("Answer:", 1)
                    rationale = parts[0].strip() if len(parts) > 1 else ""
                    answer = parts[1].strip() if len(parts) > 1 else llm_response.strip()
                else:
                    answer = llm_response.strip()
                    rationale = ""
                
                logger.info(f"Generated answer for question {i+1}")
                
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                answer = f"Unable to generate answer due to error: {str(e)}"
                rationale = ""

            # 7. Calculate score (placeholder: 1.0 for now)
            try:
                score = calculate_score(True, 1.0, 1.0)
            except Exception as e:
                logger.error(f"Scoring failed: {e}")
                score = 0.0

            # 8. Save answer to DB
            try:
                a_obj = Answer(
                    question_id=q_obj.id, 
                    answer_text=answer, 
                    rationale=rationale, 
                    clause_reference=clause_ref, 
                    score=score
                )
                db.add(a_obj)
                db.commit()
                logger.info(f"Saved answer for question {i+1} to database")
            except Exception as e:
                logger.error(f"DB save answer failed: {e}")
                db.rollback()

            # Return structured answer
            return {
                "answer": answer,
                "question": question,
                "score": str(score)  # Convert score to string to ensure compatibility
            }
        
        # Process all questions in parallel
        tasks = [process_question(i, question) for i, question in enumerate(request.questions)]
        answer_strings = await asyncio.gather(*tasks)

        db.close()
        logger.info(f"Pipeline completed successfully. Generated {len(answer_strings)} answers.")
        return HackrxResponse(answers=answer_strings)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        # Return error response with structured format
        return HackrxResponse(answers=[{
            "answer": f"Pipeline error: {str(e)}",
            "question": "Error",
            "score": "0.0"  # Use string format for score
        }])
