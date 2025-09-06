from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ResponseBase(BaseModel):
    """Base response model"""
    email_id: int
    content: str
    response_type: str = "ai_generated"  # ai_generated, manual, template
    sentiment: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None

class ResponseCreate(ResponseBase):
    """Model for creating a new response"""
    pass

class ResponseInDB(ResponseBase):
    """Response model as stored in database"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
