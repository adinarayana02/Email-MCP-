from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class PriorityType(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class EmailStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class EmailBase(BaseModel):
    sender: EmailStr
    subject: str
    body: str

class EmailCreate(EmailBase):
    email_id: str
    received_date: datetime
    thread_id: Optional[str] = None

class EmailUpdate(BaseModel):
    sentiment: Optional[SentimentType] = None
    priority: Optional[PriorityType] = None
    status: Optional[EmailStatus] = None
    processed: Optional[bool] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None

class EmailInDB(EmailBase):
    id: int
    received_date: datetime
    thread_id: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    priority: Optional[str] = None
    priority_score: Optional[float] = None
    category: Optional[str] = None
    extracted_info: Optional[str] = None
    status: str = "pending"
    assigned_to: Optional[str] = None
    tags: Optional[str] = None
    processed: bool = False
    email_id: str
    response_time_minutes: Optional[int] = None

    class Config:
        from_attributes = True

class EmailResponse(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    received_date: datetime
    thread_id: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    priority: Optional[str] = None
    priority_score: Optional[float] = None
    category: Optional[str] = None
    extracted_info: Optional[Dict[str, Any]] = None
    status: str = "pending"
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None
    processed: bool = False
    generated_response: Optional[str] = None
    response_time_minutes: Optional[int] = None

class ProcessedEmail(BaseModel):
    id: int
    sender: str
    subject: str
    body: str
    received_date: datetime
    thread_id: Optional[str] = None
    sentiment: str
    sentiment_score: float
    priority: str
    priority_score: float
    category: str
    extracted_info: Dict[str, Any]
    status: str
    assigned_to: Optional[str] = None
    tags: List[str]
    generated_response: str
    confidence_score: float
    response_time_minutes: Optional[int] = None

class EmailFilter(BaseModel):
    # Basic filters
    priority: Optional[PriorityType] = None
    sentiment: Optional[SentimentType] = None
    category: Optional[str] = None
    status: Optional[EmailStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    assigned_to: Optional[str] = None
    search_query: Optional[str] = None
    processed: Optional[bool] = None
    
    # Enhanced filters
    sender_domain: Optional[str] = None
    sender_email: Optional[str] = None
    has_attachments: Optional[bool] = None
    min_priority_score: Optional[float] = None
    min_sentiment_score: Optional[float] = None
    subject_contains: Optional[str] = None
    body_contains: Optional[str] = None
    tags: Optional[List[str]] = None
    
    # Sorting options
    sort_by: Optional[str] = "received_date"  # field to sort by
    sort_desc: Optional[bool] = True  # descending order if True

class EmailBulkUpdate(BaseModel):
    email_ids: List[int]
    status: Optional[EmailStatus] = None
    priority: Optional[PriorityType] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None