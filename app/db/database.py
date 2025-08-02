# Database connection setup

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import POSTGRES_URL

if not POSTGRES_URL:
    raise RuntimeError("POSTGRES_URL is not set. Please check your .env file and set the correct database URL.")

engine = create_engine(POSTGRES_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ORM models for document/question/answer tracking
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    source_url = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    # Relationship
    questions = relationship("Question", back_populates="document")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    asked_at = Column(DateTime, default=datetime.utcnow)
    # Relationship
    document = relationship("Document", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    clause_reference = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    extra_data = Column(JSON, nullable=True)
    # Relationship
    question = relationship("Question", back_populates="answers")
