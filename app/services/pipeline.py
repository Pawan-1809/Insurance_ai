from app.models.request import HackrxRequest
from app.models.response import HackrxResponse, AnswerItem
from app.services.document_ingestion import ingest_document
from app.services.embedding_pipeline import upsert_chunks_to_pinecone, query_pinecone
from app.services.llm_client import ask_llm
from app.services.scoring import calculate_score

from app.db.database import SessionLocal, Document, Question, Answer

import uuid
import os
import logging

logger = logging.getLogger("pipeline")
logging.basicConfig(level=logging.INFO)

async def process_query_pipeline(request: HackrxRequest) -> HackrxResponse:
    try:
        # 1. Ingest document (download/parse)
        doc_id = str(uuid.uuid4())
        try:
            chunks, file_path = ingest_document(request.documents, is_url=request.documents.startswith("http"))
        except Exception as e:
            logger.error(f"Document ingestion failed: {e}")
            raise RuntimeError(f"Document ingestion failed: {e}")

        # 2. Upsert chunks to Pinecone
        try:
            await upsert_chunks_to_pinecone(chunks, doc_id)
        except Exception as e:
            logger.error(f"Pinecone upsert failed: {e}")
            raise RuntimeError(f"Pinecone upsert failed: {e}")

        # 3. Save document to DB
        db = SessionLocal()
        try:
            doc_obj = Document(name=file_path.split(os.sep)[-1], source_url=request.documents)
            db.add(doc_obj)
            db.commit()
            db.refresh(doc_obj)
        except Exception as e:
            logger.error(f"DB save document failed: {e}")
            db.rollback()
            raise RuntimeError(f"DB save document failed: {e}")

        answer_items = []
        for q in request.questions:
            try:
                # 4. Save question to DB
                q_obj = Question(document_id=doc_obj.id, question_text=q)
                db.add(q_obj)
                db.commit()
                db.refresh(q_obj)
            except Exception as e:
                logger.error(f"DB save question failed: {e}")
                db.rollback()
                continue

            # 5. Query Pinecone for relevant chunks
            try:
                matches = await query_pinecone(q, top_k=3)
                context = "\n".join([m.get("metadata", {}).get("text", "") for m in matches])
                clause_ref = matches[0].get("id") if matches else None
            except Exception as e:
                logger.error(f"Pinecone query failed: {e}")
                context = ""
                clause_ref = None

            # 6. Use LLM to answer with rationale
            try:
                prompt = f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer with rationale and reference to the clause if possible."
                answer = ask_llm(prompt)
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                answer = "LLM error: " + str(e)

            # 7. Score (placeholder: 1.0 for now)
            try:
                score = calculate_score(True, 1.0, 1.0)
            except Exception as e:
                logger.error(f"Scoring failed: {e}")
                score = 0.0

            # 8. Save answer to DB
            try:
                a_obj = Answer(question_id=q_obj.id, answer_text=answer, rationale="", clause_reference=clause_ref, score=score)
                db.add(a_obj)
                db.commit()
            except Exception as e:
                logger.error(f"DB save answer failed: {e}")
                db.rollback()

            answer_items.append(AnswerItem(answer=answer, rationale="", clause_reference=clause_ref, score=score))

        db.close()
        return HackrxResponse(answers=answer_items)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return HackrxResponse(answers=[AnswerItem(answer=f"Pipeline error: {e}", rationale="", clause_reference=None, score=0.0)])
