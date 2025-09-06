from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db
from models import Email, Response, EmailCategory, EmailPriority, EmailSentiment
from sqlalchemy import func, and_, or_, desc, cast, Date
import random

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total_emails = db.query(func.count(Email.id)).scalar() or 0
    pending_emails = db.query(func.count(Email.id)).filter(Email.status == "pending").scalar() or 0
    resolved_emails = db.query(func.count(Email.id)).filter(Email.status == "resolved").scalar() or 0
    urgent_emails = db.query(func.count(Email.id)).filter(Email.priority == EmailPriority.HIGH).scalar() or 0
    
    # Calculate average response time in minutes
    avg_response_time = db.query(
        func.avg(
            func.extract('epoch', Email.response_timestamp - Email.received_timestamp) / 60
        )
    ).filter(Email.response_timestamp.isnot(None)).scalar() or 0
    
    # Calculate resolution rate
    resolution_rate = int((resolved_emails / total_emails * 100) if total_emails > 0 else 0)
    
    # Calculate AI accuracy (mock data for now)
    ai_accuracy = random.randint(85, 95)
    
    return {
        "total_emails": total_emails,
        "pending_emails": pending_emails,
        "resolved_emails": resolved_emails,
        "urgent_emails": urgent_emails,
        "avg_response_time": round(avg_response_time, 1),
        "resolution_rate": resolution_rate,
        "ai_accuracy": ai_accuracy
    }

@router.get("/sentiment")
async def get_sentiment_analysis(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get sentiment analysis data"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    sentiment_counts = db.query(
        Email.sentiment,
        func.count(Email.id).label("count")
    ).filter(
        Email.received_timestamp >= cutoff_date
    ).group_by(Email.sentiment).all()
    
    result = []
    for sentiment, count in sentiment_counts:
        if sentiment:
            result.append({
                "name": sentiment.value,
                "value": count,
                "color": get_sentiment_color(sentiment)
            })
    
    return result

@router.get("/priority")
async def get_priority_analysis(db: Session = Depends(get_db)):
    """Get priority analysis data"""
    priority_counts = db.query(
        Email.priority,
        func.count(Email.id).label("count")
    ).group_by(Email.priority).all()
    
    result = []
    for priority, count in priority_counts:
        if priority:
            result.append({
                "name": priority.value,
                "value": count,
                "color": get_priority_color(priority)
            })
    
    return result

@router.get("/category")
async def get_category_analysis(db: Session = Depends(get_db)):
    """Get category analysis data"""
    category_counts = db.query(
        Email.category,
        func.count(Email.id).label("count")
    ).group_by(Email.category).all()
    
    result = []
    for category, count in category_counts:
        if category:
            result.append({
                "name": category.value,
                "value": count,
                "color": get_category_color(category)
            })
    
    return result

@router.get("/performance")
async def get_performance_metrics(db: Session = Depends(get_db)):
    """Get performance metrics"""
    # Calculate average response time in minutes
    avg_response_time = db.query(
        func.avg(
            func.extract('epoch', Email.response_timestamp - Email.received_timestamp) / 60
        )
    ).filter(Email.response_timestamp.isnot(None)).scalar() or 0
    
    # Calculate average resolution time in minutes
    avg_resolution_time = db.query(
        func.avg(
            func.extract('epoch', Email.resolved_timestamp - Email.received_timestamp) / 60
        )
    ).filter(Email.resolved_timestamp.isnot(None)).scalar() or 0
    
    # Calculate satisfaction rate (mock data for now)
    satisfaction_rate = random.randint(85, 98)
    
    # Calculate daily processed emails
    today = datetime.now().date()
    daily_processed = db.query(func.count(Email.id)).filter(
        cast(Email.received_timestamp, Date) == today
    ).scalar() or 0
    
    return {
        "response_time": round(avg_response_time, 1),
        "resolution_time": round(avg_resolution_time, 1),
        "satisfaction_rate": satisfaction_rate,
        "daily_processed": daily_processed,
        "daily_target": 100
    }

@router.get("/timeseries")
async def get_timeseries_data(days: str = Query("30"), db: Session = Depends(get_db)):
    """Get time series data for email metrics"""
    try:
        days_int = int(days.replace("d", ""))
    except ValueError:
        days_int = 30
    
    cutoff_date = datetime.now() - timedelta(days=days_int)
    
    # Get dates for the period
    date_range = []
    current_date = cutoff_date
    end_date = datetime.now()
    
    while current_date <= end_date:
        date_range.append(current_date.date())
        current_date += timedelta(days=1)
    
    result = []
    
    for date in date_range:
        next_date = date + timedelta(days=1)
        
        # Get counts for this date
        total_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date
        ).scalar() or 0
        
        resolved_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.status == "resolved"
        ).scalar() or 0
        
        pending_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.status == "pending"
        ).scalar() or 0
        
        # Get sentiment counts
        positive_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.sentiment == EmailSentiment.POSITIVE
        ).scalar() or 0
        
        neutral_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.sentiment == EmailSentiment.NEUTRAL
        ).scalar() or 0
        
        negative_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.sentiment == EmailSentiment.NEGATIVE
        ).scalar() or 0
        
        # Get priority counts
        high_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.priority == EmailPriority.HIGH
        ).scalar() or 0
        
        medium_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.priority == EmailPriority.MEDIUM
        ).scalar() or 0
        
        low_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.priority == EmailPriority.LOW
        ).scalar() or 0
        
        # Get category counts (simplified for common categories)
        technical_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.category == EmailCategory.TECHNICAL_SUPPORT
        ).scalar() or 0
        
        billing_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.category == EmailCategory.BILLING
        ).scalar() or 0
        
        general_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.category == EmailCategory.GENERAL_INQUIRY
        ).scalar() or 0
        
        complaint_count = db.query(func.count(Email.id)).filter(
            cast(Email.received_timestamp, Date) == date,
            Email.category == EmailCategory.COMPLAINT
        ).scalar() or 0
        
        result.append({
            "date": date.strftime("%Y-%m-%d"),
            "total": total_count,
            "resolved": resolved_count,
            "pending": pending_count,
            "positive": positive_count,
            "neutral": neutral_count,
            "negative": negative_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
            "technical": technical_count,
            "billing": billing_count,
            "general": general_count,
            "complaint": complaint_count
        })
    
    return result

@router.get("/response-time")
async def get_response_time_metrics(db: Session = Depends(get_db)):
    """Get response time metrics by category"""
    # Get average response time by category
    category_response_times = db.query(
        Email.category,
        func.avg(func.extract('epoch', Email.response_timestamp - Email.received_timestamp) / 60).label("avg_time")
    ).filter(
        Email.response_timestamp.isnot(None)
    ).group_by(Email.category).all()
    
    result = []
    
    # Define target response times by category (in minutes)
    target_times = {
        EmailCategory.TECHNICAL_SUPPORT: 30,
        EmailCategory.BILLING: 20,
        EmailCategory.GENERAL_INQUIRY: 15,
        EmailCategory.COMPLAINT: 15,
        EmailCategory.FEATURE_REQUEST: 48,
        EmailCategory.SALES: 25,
        EmailCategory.OTHER: 30
    }
    
    for category, avg_time in category_response_times:
        if category:
            result.append({
                "name": category.value,
                "value": round(avg_time, 1),
                "target": target_times.get(category, 30),
                "color": get_category_color(category)
            })
    
    return result

@router.get("/keywords")
async def get_top_keywords(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """Get top keywords from emails (mock data for now)"""
    # This would normally extract keywords from email content using NLP
    # For now, return mock data
    mock_keywords = [
        {"keyword": "login", "count": random.randint(20, 50), "sentiment": "negative"},
        {"keyword": "password", "count": random.randint(15, 40), "sentiment": "neutral"},
        {"keyword": "billing", "count": random.randint(15, 35), "sentiment": "negative"},
        {"keyword": "thank", "count": random.randint(10, 30), "sentiment": "positive"},
        {"keyword": "help", "count": random.randint(10, 25), "sentiment": "neutral"},
        {"keyword": "error", "count": random.randint(8, 20), "sentiment": "negative"},
        {"keyword": "great", "count": random.randint(5, 15), "sentiment": "positive"},
        {"keyword": "issue", "count": random.randint(5, 15), "sentiment": "negative"},
        {"keyword": "support", "count": random.randint(5, 15), "sentiment": "neutral"},
        {"keyword": "feature", "count": random.randint(3, 10), "sentiment": "positive"},
    ]
    
    return mock_keywords[:limit]

@router.get("/distribution")
async def get_email_distribution(type: str = Query("hourly"), db: Session = Depends(get_db)):
    """Get email distribution by hour or day of week"""
    if type == "hourly":
        # Get distribution by hour of day
        hour_distribution = db.query(
            func.extract('hour', Email.received_timestamp).label("hour"),
            func.count(Email.id).label("count")
        ).group_by("hour").order_by("hour").all()
        
        result = []
        for hour, count in hour_distribution:
            result.append({
                "hour": int(hour),
                "count": count
            })
        
        # Fill in missing hours with zero
        hours = {item["hour"]: item["count"] for item in result}
        complete_result = []
        for hour in range(24):
            complete_result.append({
                "hour": hour,
                "count": hours.get(hour, 0)
            })
        
        return complete_result
    
    elif type == "daily":
        # Get distribution by day of week
        day_distribution = db.query(
            func.extract('dow', Email.received_timestamp).label("day"),
            func.count(Email.id).label("count")
        ).group_by("day").order_by("day").all()
        
        result = []
        day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
        for day, count in day_distribution:
            result.append({
                "day": day_names[int(day)],
                "day_num": int(day),
                "count": count
            })
        
        # Fill in missing days with zero
        days = {item["day_num"]: item["count"] for item in result}
        complete_result = []
        for day in range(7):
            complete_result.append({
                "day": day_names[day],
                "day_num": day,
                "count": days.get(day, 0)
            })
        
        return complete_result
    
    else:
        raise HTTPException(status_code=400, detail="Invalid distribution type. Use 'hourly' or 'daily'.")

# Helper functions for color coding
def get_sentiment_color(sentiment):
    """Get color for sentiment"""
    colors = {
        EmailSentiment.POSITIVE: "#10B981",  # green
        EmailSentiment.NEUTRAL: "#6B7280",   # gray
        EmailSentiment.NEGATIVE: "#EF4444"   # red
    }
    return colors.get(sentiment, "#6B7280")

def get_priority_color(priority):
    """Get color for priority"""
    colors = {
        EmailPriority.HIGH: "#EF4444",      # red
        EmailPriority.MEDIUM: "#F97316",    # orange
        EmailPriority.LOW: "#10B981"        # green
    }
    return colors.get(priority, "#6B7280")

def get_category_color(category):
    """Get color for category"""
    colors = {
        EmailCategory.TECHNICAL_SUPPORT: "#3B82F6",  # blue
        EmailCategory.BILLING: "#10B981",           # green
        EmailCategory.GENERAL_INQUIRY: "#6B7280",    # gray
        EmailCategory.COMPLAINT: "#F97316",          # orange
        EmailCategory.FEATURE_REQUEST: "#8B5CF6",    # purple
        EmailCategory.SALES: "#EC4899",              # pink
        EmailCategory.OTHER: "#6B7280"                # gray
    }
    return colors.get(category, "#6B7280")