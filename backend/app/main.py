from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import json
from datetime import datetime, timedelta
import logging
import threading
import schedule
import time
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base

from app.config import settings
from app.models.email import EmailResponse, ProcessedEmail
# Import services first
from app.services.csv_data_service import CSVDataService
from app.services.ai_service import AIService

# Initialize services
csv_data_service = CSVDataService()
ai_service = AIService()

# Import routers after services are initialized
from app.routers.emails import router as emails_router
from app.routers.analytics import router as analytics_router

# Initialize logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Communication Assistant for Email Management",
    version=settings.app_version,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Services are already initialized above

# Include routers
app.include_router(emails_router, prefix="/api/v1/emails", tags=["emails"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])

# Mount static files directory to serve CSV and JSON files directly
app.mount("/api/v1/data", StaticFiles(directory="data"), name="data")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/v1/generate-dashboard-data")
async def generate_dashboard_data():
    """Endpoint to manually trigger dashboard data generation"""
    try:
        # Refresh CSV data and regenerate dashboard data
        csv_data_service.refresh()
        csv_data_service.generate_dashboard_data()
        return {"status": "success", "message": "Dashboard data regenerated successfully"}
    except Exception as e:
        logger.error(f"Error generating dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize application and start background tasks"""
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Load CSV data and generate dashboard data
        csv_data_service.load()
        csv_data_service.generate_dashboard_data()
        logger.info("CSV data loaded and dashboard data generated successfully")
        
        # Start background tasks
        start_background_tasks()
        logger.info("Background tasks started successfully")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

# Define the dashboard data generation job
async def generate_dashboard_data_job():
    """Background job to generate dashboard data from CSV"""
    try:
        # Refresh CSV data and regenerate dashboard data
        csv_data_service.refresh()
        csv_data_service.generate_dashboard_data()
        logger.info("Dashboard data regenerated successfully")
    except Exception as e:
        logger.error(f"Error in dashboard data generation job: {e}")

def start_background_tasks():
    """Start background tasks for data processing"""
    def run_scheduler():
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                time.sleep(60)  # Continue after error
    
    # Schedule dashboard data generation every 5 minutes
    schedule.every(5).minutes.do(generate_dashboard_data_job)
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Background scheduler started")

def fetch_and_process_emails_job():
    """Background job to fetch and process emails"""
    try:
        logger.info("Starting email fetch and process job")
        db = None if settings.use_dataset else next(get_db())
        
        # Fetch emails from source
        if settings.use_dataset:
            new_emails = email_service.load_emails_from_dataset()
            saved_count = len(new_emails)
        else:
            new_emails = email_service.fetch_emails(days_back=1)
            saved_count = email_service.save_emails_to_db(new_emails, db)
        
        if saved_count > 0:
            # Process unprocessed emails
            if settings.use_dataset:
                # In dataset mode, process the in-memory list
                unprocessed_emails = []
                # Create a light adapter dicts to mimic ORM fields
                for e in new_emails:
                    class Obj: pass
                    obj = Obj()
                    obj.id = 0
                    obj.sender = e['sender']
                    obj.subject = e['subject']
                    obj.body = e['body']
                    obj.received_date = e['received_date']
                    obj.processed = False
                    obj.sentiment = None
                    obj.sentiment_score = None
                    obj.priority = None
                    obj.priority_score = None
                    obj.category = None
                    obj.extracted_info = None
                    obj.status = 'pending'
                    obj.assigned_to = None
                    obj.response_time_minutes = None
                    unprocessed_emails.append(obj)
            else:
                unprocessed_emails = db.query(Email).filter(Email.processed == False).all()
            
            for email_obj in unprocessed_emails:
                try:
                    # Analyze sentiment using dedicated service
                    sentiment_result = sentiment_service.analyze_sentiment(
                        email_obj.subject + " " + email_obj.body
                    )
                    sentiment = sentiment_result.get("sentiment", "neutral")
                    sentiment_score = sentiment_result.get("confidence", 0.5)
                    
                    # Determine priority using dedicated service
                    priority_result = priority_service.determine_priority(
                        email_obj.subject, email_obj.body, email_obj.sender
                    )
                    priority = priority_result.get("priority", "normal")
                    priority_score = priority_result.get("score", 0.5)
                    
                    # Categorize email
                    category = ai_service.categorize_email(email_obj.subject, email_obj.body)
                    
                    # Extract information
                    extracted_info = ai_service.extract_information(
                        email_obj.subject, email_obj.body, email_obj.sender
                    )
                    
                    # Generate response
                    generated_response, confidence = ai_service.generate_response(
                        email_obj.subject, email_obj.body, email_obj.sender,
                        sentiment, priority, category, extracted_info
                    )
                    
                    # Update email record
                    email_obj.sentiment = sentiment
                    email_obj.sentiment_score = sentiment_score
                    email_obj.priority = priority
                    email_obj.priority_score = priority_score
                    email_obj.category = category
                    email_obj.extracted_info = json.dumps(extracted_info)
                    email_obj.processed = True
                    
                    # Process response (no need to save to database)
                    
                except Exception as e:
                    logger.error(f"Error processing email {email_obj.id}: {e}")
                    continue
            
            logger.info(f"Processed {len(unprocessed_emails)} emails")
        
    except Exception as e:
        logger.error(f"Error in email fetch job: {e}")

def update_analytics_job():
    """Background job to update analytics"""
    try:
        if settings.use_dataset:
            # Skip DB analytics when running with dataset only
            return
        db = next(get_db())
        
        # Get current date
        today = datetime.now().date()
        
        # Calculate analytics for today
        total_emails = db.query(Email).filter(
            Email.received_date >= today
        ).count()
        
        urgent_emails = db.query(Email).filter(
            Email.received_date >= today,
            Email.priority == 'urgent'
        ).count()
        
        positive_emails = db.query(Email).filter(
            Email.received_date >= today,
            Email.sentiment == 'positive'
        ).count()
        
        negative_emails = db.query(Email).filter(
            Email.received_date >= today,
            Email.sentiment == 'negative'
        ).count()
        
        neutral_emails = db.query(Email).filter(
            Email.received_date >= today,
            Email.sentiment == 'neutral'
        ).count()
        
        resolved_emails = db.query(Response).join(Email).filter(
            Email.received_date >= today,
            Response.is_sent == True
        ).count()
        
        pending_emails = total_emails - resolved_emails
        
        # Check if analytics record exists for today
        existing_analytics = db.query(Analytics).filter(
            Analytics.date >= today
        ).first()
        
        if existing_analytics:
            # Update existing record
            existing_analytics.total_emails = total_emails
            existing_analytics.urgent_emails = urgent_emails
            existing_analytics.positive_sentiment = positive_emails
            existing_analytics.negative_sentiment = negative_emails
            existing_analytics.neutral_sentiment = neutral_emails
            existing_analytics.emails_resolved = resolved_emails
            existing_analytics.emails_pending = pending_emails
        else:
            # Create new record
            analytics_obj = Analytics(
                date=datetime.now(),
                total_emails=total_emails,
                urgent_emails=urgent_emails,
                positive_sentiment=positive_emails,
                negative_sentiment=negative_emails,
                neutral_sentiment=neutral_emails,
                emails_resolved=resolved_emails,
                emails_pending=pending_emails
            )
            db.add(analytics_obj)
        
        db.commit()
        logger.info("Analytics updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating analytics: {e}")
    finally:
        if 'db' in locals():
            db.close()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Communication Assistant API",
        "version": settings.app_version,
        "status": "active",
        "timestamp": datetime.now()
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    try:
        # CSV data service status
        csv_status = "active" if os.path.exists("data/Support_Emails_Dataset.csv") else "not found"
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "services": {
                "csv_data_service": csv_status,
                "email_service": "active",
                "ai_service": "active",
                "sentiment_service": "active",
                "priority_service": "active"
            },
            "version": settings.app_version
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/api/v1/process-emails")
async def trigger_email_processing(background_tasks: BackgroundTasks):
    """Manually trigger email processing"""
    try:
        # Validate dataset configuration when in dataset mode
        if settings.use_dataset:
            ds_path = settings.dataset_path or ""
            if not ds_path or not os.path.exists(ds_path):
                raise HTTPException(
                    status_code=400,
                    detail=f"Dataset path not found: {ds_path}. Set DATASET_PATH or update settings."
                )
        background_tasks.add_task(fetch_and_process_emails_job)
        return {
            "message": "Email processing triggered successfully",
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Failed to trigger email processing: {e}")
        # Fallback: try starting in separate thread to avoid background task limitations
        try:
            threading.Thread(target=fetch_and_process_emails_job, daemon=True).start()
            return {
                "message": "Email processing started in background thread",
                "timestamp": datetime.now()
            }
        except Exception as e2:
            logger.error(f"Fallback trigger also failed: {e2}")
            raise HTTPException(
                status_code=500,
                detail="Failed to start email processing. Check server logs."
            )

@app.get("/api/v1/emails/priority-queue")
async def get_priority_queue(db: Session = Depends(get_db)):
    """Get emails sorted by priority (urgent first)"""
    try:
        if settings.use_dataset:
            # Build queue from dataset
            emails = email_service.load_emails_from_dataset()
            queue = []
            for e in emails:
                sentiment_result = sentiment_service.analyze_sentiment(e['subject'] + " " + e['body'])
                pr = priority_service.determine_priority(e['subject'], e['body'], e['sender'])
                category = ai_service.categorize_email(e['subject'], e['body'])
                extracted_info = ai_service.extract_information(e['subject'], e['body'], e['sender'])
                generated_response, confidence = ai_service.generate_response(
                    e['subject'], e['body'], e['sender'],
                    sentiment_result.get("sentiment","neutral"), pr.get("priority","normal"), category, extracted_info
                )
                email_data = ProcessedEmail(
                    id=0,
                    sender=e['sender'],
                    subject=e['subject'],
                    body=e['body'],
                    received_date=e['received_date'],
                    sentiment=sentiment_result.get("sentiment","neutral"),
                    sentiment_score=sentiment_result.get("confidence",0.0),
                    priority=pr.get("priority","normal"),
                    priority_score=pr.get("score",0.0),
                    category=category,
                    extracted_info=extracted_info,
                    status="pending",
                    assigned_to=None,
                    tags=[],
                    generated_response=generated_response,
                    confidence_score=confidence,
                    response_time_minutes=None
                )
                queue.append(email_data)
            # urgent first, then normal/high/low by received_date desc
            queue.sort(key=lambda x: (0 if x.priority == 'urgent' else 1, -int(x.received_date.timestamp())))
            urgent_count = sum(1 for q in queue if q.priority == 'urgent')
            normal_count = len(queue) - urgent_count
            return {
                "total_emails": len(queue),
                "urgent_count": urgent_count,
                "normal_count": normal_count,
                "emails": queue,
                "timestamp": datetime.now()
            }
        # Use CSV data service instead of database
        csv_data_service.refresh()
        all_emails = csv_data_service.get_all_emails()
        
        # Sort emails by priority and date
        urgent_emails = [email for email in all_emails if email.get('priority') == 'urgent']
        normal_emails = [email for email in all_emails if email.get('priority') != 'urgent']
        
        # Sort by received date (newest first)
        urgent_emails.sort(key=lambda x: x.get('received_date', datetime.now()), reverse=True)
        normal_emails.sort(key=lambda x: x.get('received_date', datetime.now()), reverse=True)
        
        # Combine lists (urgent first)
        all_emails = urgent_emails + normal_emails
        
        # Format response
        email_queue = []
        for email_obj in all_emails:
                # Process email data from CSV
            response = email_obj.get('generated_response', '')
            
            extracted_info = email_obj.get('extracted_info', {})
            
            email_data = ProcessedEmail(
                id=email_obj.get('id', 0),
                sender=email_obj.get('sender', ''),
                subject=email_obj.get('subject', ''),
                body=email_obj.get('body', ''),
                received_date=email_obj.get('received_date', datetime.now()),
                sentiment=email_obj.get('sentiment', 'neutral'),
                sentiment_score=email_obj.get('sentiment_score', 0.0),
                priority=email_obj.get('priority', 'normal'),
                priority_score=email_obj.get('priority_score', 0.0),
                category=email_obj.get('category', ''),
                extracted_info=extracted_info,
                status=email_obj.get('status', 'pending'),
                assigned_to=email_obj.get('assigned_to', None),
                tags=email_obj.get('tags', []),
                generated_response=response,
                confidence_score=email_obj.get('confidence_score', 0.0),
                response_time_minutes=email_obj.get('response_time_minutes', None)
            )
            email_queue.append(email_data)
        
        return {
            "total_emails": len(email_queue),
            "urgent_count": len(urgent_emails),
            "normal_count": len(normal_emails),
            "emails": email_queue,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error getting priority queue: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving priority queue: {str(e)}"
        )

@app.get("/api/v1/system/status")
async def get_system_status():
    """Get system status and configuration info"""
    try:
        return {
            "status": "operational",
            "timestamp": datetime.now(),
            "configuration": {
                "app_name": settings.app_name,
                "version": settings.app_version,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "debug_mode": settings.debug,
                "database_url": settings.database_url.split("/")[-1] if settings.database_url else "not configured",
                "use_dataset": settings.use_dataset,
                "dataset_path": settings.dataset_path,
                "email_service": "configured" if settings.email_username else "not configured",
                "ai_service": "configured" if settings.openai_api_key else "not configured"
            },
            "services": {
                "database": "connected",
                "email_service": "active",
                "ai_service": "active"
            }
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving system status: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )