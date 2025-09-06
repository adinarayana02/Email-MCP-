from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from app.config import settings

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Configure engine with SQLite-specific connect args only when applicable
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(255), index=True)
    subject = Column(String(500))
    body = Column(Text)
    received_date = Column(DateTime, default=datetime.utcnow)
    thread_id = Column(String(255), nullable=True, index=True)
    sentiment = Column(String(50))  # positive, negative, neutral
    sentiment_score = Column(Float)
    priority = Column(String(50))  # urgent, high, normal, low
    priority_score = Column(Float)
    category = Column(String(100))
    extracted_info = Column(Text)  # JSON string
    status = Column(String(50), default="pending")  # pending, in_progress, resolved, closed
    assigned_to = Column(String(255), nullable=True)
    tags = Column(Text, nullable=True)  # JSON string of tags
    processed = Column(Boolean, default=False)
    email_id = Column(String(255), unique=True)  # Unique email identifier
    response_time_minutes = Column(Integer, nullable=True)
    
class Response(Base):
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, index=True)
    generated_response = Column(Text)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    confidence_score = Column(Float)
    response_type = Column(String(50), default="ai_generated")  # ai_generated, manual, template

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    total_emails = Column(Integer, default=0)
    urgent_emails = Column(Integer, default=0)
    high_priority_emails = Column(Integer, default=0)
    positive_sentiment = Column(Integer, default=0)
    negative_sentiment = Column(Integer, default=0)
    neutral_sentiment = Column(Integer, default=0)
    emails_resolved = Column(Integer, default=0)
    emails_pending = Column(Integer, default=0)
    emails_in_progress = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)
    satisfaction_score = Column(Float, default=0.0)

class EmailThread(Base):
    __tablename__ = "email_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String(255), unique=True, index=True)
    subject = Column(String(500))
    status = Column(String(50), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    email_count = Column(Integer, default=1)
    last_response_date = Column(DateTime, nullable=True)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()