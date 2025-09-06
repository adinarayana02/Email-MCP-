from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime, timedelta
from enum import Enum

from app.config import settings
from app.services.ai_service import AIService
from app.models.email import EmailResponse, ProcessedEmail, EmailUpdate, EmailFilter, EmailBulkUpdate
from app.services.csv_data_service import CSVDataService

router = APIRouter()
csv_data_service = CSVDataService()
ai_service = AIService()
logger = logging.getLogger(__name__)


class ResponseTextPayload(BaseModel):
    response_text: Optional[str] = None


class ImportPayload(BaseModel):
    file_path: str
    file_type: Optional[str] = None  # csv | excel


class ResponseTone(str, Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    EMPATHETIC = "empathetic"
    TECHNICAL = "technical"
    SIMPLE = "simple"


class ContextAwareResponsePayload(BaseModel):
    email_id: int
    context_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context information to enhance response generation"
    )
    response_tone: Optional[ResponseTone] = Field(
        default=ResponseTone.PROFESSIONAL,
        description="Tone to use for the generated response"
    )
    include_knowledge_base: Optional[bool] = Field(
        default=True,
        description="Whether to include knowledge base information in response generation"
    )

@router.get("/fetch", response_model=List[ProcessedEmail])
async def fetch_emails(
    skip: int = 0,
    limit: int = 100,
    filter_params: Optional[EmailFilter] = None,
):
    """Fetch emails with optional filtering"""
    try:
        # Use CSV data service to get emails
        emails = csv_data_service.get_emails(skip=skip, limit=limit, filter_params=filter_params)
        return emails
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_emails():
    """List emails for UI from CSV data"""
    try:
        # Refresh CSV data
        csv_data_service.refresh()
        
        # Get all emails from CSV
        emails = csv_data_service.get_all_emails()
        
        # Return the emails directly
        return {"emails": emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing emails: {str(e)}")

@router.get("/{email_id}/extract-info")
async def extract_email_information(email_id: str):
    """Extract structured information from an email for enhanced analytics"""
    try:
        # Get the email from CSV data
        csv_data_service.refresh()
        emails = csv_data_service.get_all_emails()
        email = next((e for e in emails if e.get('email_id') == email_id), None)
        if not email:
            raise HTTPException(status_code=404, detail=f"Email with ID {email_id} not found")
        
        # Extract structured information
        extracted_info = {
            "request_type": email.get('category', ''),
            "urgency_level": email.get('priority', 'normal'),
            "sentiment": email.get('sentiment', 'neutral'),
            "key_points": [],
            "entities": []
        }
        
        return {
            "email_id": email_id,
            "extracted_info": extracted_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting information: {str(e)}")

@router.post("/batch-extract")
async def batch_extract_information(email_ids: List[int]):
    """Extract structured information from multiple emails for batch processing"""
    try:
        results = []
        
        # Get all emails from CSV data
        csv_data_service.refresh()
        emails = csv_data_service.get_all_emails()
        
        for email_id in email_ids:
            # Get the email from CSV data
            email = next((e for e in emails if e.get('id') == email_id), None)
            if not email:
                results.append({
                    "email_id": email_id,
                    "status": "error",
                    "message": f"Email with ID {email_id} not found"
                })
                continue
            
            # Extract structured information
            try:
                # Use existing data from CSV instead of extracting
                extracted_info = {
                    "request_type": email.get('category', ''),
                    "urgency_level": email.get('priority', 'normal'),
                    "sentiment": email.get('sentiment', 'neutral'),
                    "key_points": [],
                    "entities": []
                }
                
                # No need to update email or save to database since we're using CSV
                
                results.append({
                    "email_id": email_id,
                    "status": "success",
                    "extracted_info": extracted_info
                })
            except Exception as e:
                results.append({
                    "email_id": email_id,
                    "status": "error",
                    "message": str(e)
                })
        
        return {
            "total": len(email_ids),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in batch extraction: {str(e)}")

@router.post("/fetch/advanced")
async def fetch_emails_advanced(
    days: Optional[int] = 1,
    max_emails: Optional[int] = 100,
    sender_domain: Optional[str] = None,
    subject_keywords: Optional[List[str]] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """Fetch emails with comprehensive filtering options
    
    Args:
        days: Number of days to look back for emails
        max_emails: Maximum number of emails to fetch
        sender_domain: Filter emails by sender domain
        subject_keywords: Filter emails containing these keywords in subject
        category: Filter by email category
        priority: Filter by email priority
        status: Filter by email status
        search: Search term for email content
    """
    try:
        # Refresh CSV data
        csv_data_service.refresh()
        
        # Create filter parameters
        filter_params = EmailFilter(
            category=category,
            priority=priority,
            status=status,
            search_term=search
        ) if any([category, priority, status, search]) else None
        
        # Get emails with filters
        emails = csv_data_service.get_emails(skip=0, limit=max_emails, filter_params=filter_params)
        
        # Apply additional filters
        if sender_domain or subject_keywords:
            filtered_emails = []
            for email in emails:
                include = True
                
                # Filter by sender domain
                if sender_domain and email.sender:
                    if sender_domain.lower() not in email.sender.lower():
                        include = False
                
                # Filter by subject keywords
                if subject_keywords and email.subject:
                    if not any(keyword.lower() in email.subject.lower() for keyword in subject_keywords):
                        include = False
                
                if include:
                    filtered_emails.append(email)
            
            emails = filtered_emails
        
        return {
            "message": f"Found {len(emails)} emails matching criteria",
            "emails": emails,
            "count": len(emails)
        }
    except Exception as e:
        logger.error(f"Error in advanced email fetch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{email_id}")
async def update_email(email_id: int, email_update: EmailUpdate):
    """Update an email's properties"""
    try:
        # Update the email in CSV data
        updated_email = csv_data_service.update_email(email_id, email_update.dict(exclude_unset=True))
        
        if not updated_email:
            raise HTTPException(status_code=404, detail=f"Email with ID {email_id} not found")
        
        return updated_email
    except Exception as e:
        logger.error(f"Error updating email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
@router.post("/bulk-update")
async def bulk_update_emails(bulk_update: EmailBulkUpdate):
    """Update multiple emails at once"""
    try:
        results = []
        for email_id in bulk_update.email_ids:
            try:
                # Update each email in CSV data
                updated_email = csv_data_service.update_email(
                    email_id, 
                    bulk_update.update_data.dict(exclude_unset=True)
                )
                
                if updated_email:
                    results.append({
                        "email_id": email_id,
                        "status": "success"
                    })
                else:
                    results.append({
                        "email_id": email_id,
                        "status": "error",
                        "message": f"Email with ID {email_id} not found"
                    })
            except Exception as e:
                results.append({
                    "email_id": email_id,
                    "status": "error",
                    "message": str(e)
                })
        
        return {
            "total": len(bulk_update.email_ids),
            "successful": sum(1 for r in results if r["status"] == "success"),
            "failed": sum(1 for r in results if r["status"] == "error"),
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in bulk update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{email_id}/generate-context-aware-response")
async def generate_context_aware_response(
    email_id: int,
    payload: ContextAwareResponsePayload
):
    """Generate a context-aware response for an existing email with customizable tone and additional context"""
    try:
        # Get the email from CSV data
        csv_data_service.refresh()
        emails = csv_data_service.get_all_emails()
        email = next((e for e in emails if e.id == email_id), None)
        
        if not email:
            raise HTTPException(status_code=404, detail=f"Email with ID {email_id} not found")
        
        # Generate response using AI service
        response_text, confidence = ai_service.generate_context_aware_response(
            email.subject, email.body, email.sender,
            email.sentiment, email.priority, email.category,
            {}, # extracted info
            payload.context_data, 
            str(payload.response_tone), 
            payload.include_knowledge_base
        )
        
        # Update the email with the response
        updated_email = csv_data_service.update_email(
            email_id,
            {"response": response_text, "status": "responded"}
        )
        
        return {
            "email_id": email_id,
            "response_text": response_text,
            "confidence": confidence,
            "tone_used": payload.response_tone,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error generating context-aware response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
        
        # Initialize services
        ai_service = AIService()
        
        # Parse extracted info
        extracted_info = {}
        if email.get('extracted_info'):
            try:
                extracted_info = json.loads(email.get('extracted_info'))
            except json.JSONDecodeError:
                logger.warning(f"Could not parse extracted_info for email {email_id}")
        
        # Generate context-aware response
        response_text, confidence = ai_service.generate_context_aware_response(
            email.get('subject', ''), email.get('body', ''), email.get('sender', ''),
            email.get('sentiment', 'neutral'), email.get('priority', 'normal'), email.get('category', ''),
            extracted_info, payload.context_data, 
            str(payload.response_tone), payload.include_knowledge_base
        )
        
        # Since we're using CSV data, we don't need to save the response to a database
        # We'll just return the generated response
        
        return {
            "email_id": email_id,
            "response": response_text,
            "confidence": confidence,
            "tone_used": str(payload.response_tone),
            "context_data_included": bool(payload.context_data),
            "knowledge_base_included": payload.include_knowledge_base
        }
        
    except Exception as e:
        logger.error(f"Error generating context-aware response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@router.post("/{email_id}/send-response")
async def send_email_response(
    email_id: int,
    payload: ResponseTextPayload
):
    """Send a response to an email"""
    try:
        # Get the email from CSV data
        csv_data_service.refresh()
        emails = csv_data_service.get_all_emails()
        email = next((e for e in emails if e.get('id') == email_id), None)
        if not email:
            raise HTTPException(status_code=404, detail=f"Email with ID {email_id} not found")
        
        # Use the provided response text
        response_text = payload.response_text
        if not response_text:
            raise HTTPException(status_code=400, detail="No response text provided")
            
        success = email_service.send_response(
            to_email=email.get('sender', ''),
            subject=f"Re: {email.get('subject', '')}",
            body=response_text,
            thread_id=email.get('thread_id', '')
        )
        if success:
            return {"message": "Response sent successfully", "email_id": email_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to send response")
        
    except Exception as e:
        logger.error(f"Error sending response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending response: {str(e)}")