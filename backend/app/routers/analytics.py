from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from datetime import datetime, timedelta
import json
import os

from app.config import settings
from app.services.csv_data_service import CSVDataService

# Initialize service
csv_data_service = CSVDataService()

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics from CSV data"""
    try:
        # Check if dashboard data JSON exists
        dashboard_path = os.path.join('data', 'dashboard_data.json')
        if os.path.exists(dashboard_path):
            # Read dashboard data from JSON file
            with open(dashboard_path, 'r') as f:
                dashboard_data = json.load(f)
            return dashboard_data
        
        # If dashboard data doesn't exist, generate it
        csv_data_service.refresh()
        csv_data_service.generate_dashboard_data()
        
        # Read the newly generated dashboard data
        with open(dashboard_path, 'r') as f:
            dashboard_data = json.load(f)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting dashboard stats: {str(e)}")

@router.get("/dashboard-stats")
async def get_dashboard_statistics():
    """Get dashboard statistics from CSV data"""
    try:
        # Process data
        csv_data_service.refresh()
        emails = csv_data_service.get_all()
        
        # Calculate metrics
        total_emails = len(emails)
        processed_emails = sum(1 for e in emails if e.get('processed', False))
        processing_rate = (processed_emails / total_emails * 100) if total_emails > 0 else 0
        
        # Calculate weekly data
        weekly_data = []
        # Add weekly data calculation here
        
        # Calculate response quality
        response_quality = 85  # Example value
        
        return {
            "response_quality": response_quality,
            "processing": {
                "total_emails": total_emails,
                "processed_emails": processed_emails,
                "processing_rate": round(processing_rate, 2)
            },
            "trends": {
                "weekly_emails": weekly_data
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard stats: {str(e)}")

@router.get("/sentiment-analysis")
async def get_sentiment_analysis(days: int = 7):
    """Get sentiment analysis over specified days from CSV data"""
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Refresh CSV data
        csv_data_service.refresh()
        emails = csv_data_service.get_all()
        
        # Get sentiment data by day
        sentiment_data = []
        for i in range(days):
            date = end_date - timedelta(days=i)
            
            # Filter emails for this date
            day_emails = [e for e in emails if e.get('received_date').date() == date]
            
            day_data = {
                "date": date.isoformat(),
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }
            
            # Count sentiments for this date
            for email in day_emails:
                sentiment = email.get('sentiment', 'neutral')
                if sentiment in day_data:
                    day_data[sentiment] += 1
            
            sentiment_data.append(day_data)
        
        # Overall sentiment summary
        total_summary = {"positive": 0, "negative": 0, "neutral": 0}
        for email in emails:
            if email.get('received_date').date() >= start_date:
                sentiment = email.get('sentiment', 'neutral')
                if sentiment in total_summary:
                    total_summary[sentiment] += 1
        
        return {
            "period": f"{days} days",
            "daily_sentiment": sentiment_data,
            "total_summary": total_summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sentiment analysis: {str(e)}")

@router.get("/priority-analysis")
async def get_priority_analysis():
    """Get priority analysis and urgent email handling stats from CSV data"""
    try:
        # Refresh CSV data
        csv_data_service.refresh()
        emails = csv_data_service.get_all()
        
        # Overall priority distribution
        priority_counts = {"urgent": 0, "high": 0, "normal": 0, "low": 0}
        for email in emails:
            priority = email.get('priority')
            if priority and priority in priority_counts:
                priority_counts[priority] += 1
        
        # Urgent emails handling stats
        urgent_emails = [e for e in emails if e.get('priority') == 'urgent']
        urgent_with_responses = sum(1 for e in urgent_emails if e.get('response'))
        urgent_resolved = sum(1 for e in urgent_emails if e.get('response') and e.get('response', {}).get('is_sent', False))
        
        # Priority by category
        category_priority_map = {}
        for email in emails:
            category = email.get('category')
            priority = email.get('priority')
            if category and priority:
                if category not in category_priority_map:
                    category_priority_map[category] = {"urgent": 0, "high": 0, "normal": 0, "low": 0}
                category_priority_map[category][priority] += 1
        
        # Response time by priority (mock data for demo)
        response_times = {
            "urgent": "1.2 hours",
            "normal": "4.8 hours"
        }
        
        return {
            "priority_distribution": priority_counts,
            "urgent_handling": {
                "total_urgent": len(urgent_emails),
                "with_responses": urgent_with_responses,
                "resolved": urgent_resolved,
                "pending": len(urgent_emails) - urgent_resolved
            },
            "priority_by_category": category_priority_map,
            "avg_response_times": response_times
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving priority analysis: {str(e)}")

@router.get("/category-breakdown")
async def get_category_breakdown():
    """Get detailed breakdown by email categories from CSV data"""
    try:
        # Refresh CSV data
        csv_data_service.refresh()
        emails = csv_data_service.get_all()
        
        # Get unique categories
        categories = {}
        for email in emails:
            category = email.get('category')
            if not category:
                continue
                
            if category not in categories:
                categories[category] = {
                    "total": 0,
                    "urgent": 0,
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "resolved": 0,
                    "pending": 0
                }
                
            # Count emails by category
            categories[category]["total"] += 1
            
            # Count by priority
            if email.get('priority') == 'urgent':
                categories[category]["urgent"] += 1
                
            # Count by sentiment
            sentiment = email.get('sentiment', 'neutral')
            if sentiment in ["positive", "negative", "neutral"]:
                categories[category][sentiment] += 1
                
            # Count responses
            if email.get('response'):
                if email.get('response', {}).get('is_sent', False):
                    categories[category]["resolved"] += 1
                else:
                    categories[category]["pending"] += 1
        
        # Format category breakdown
        category_breakdown = []
        for category, stats in categories.items():
            category_breakdown.append({
                "category": category,
                "total_emails": stats["total"],
                "urgent_emails": stats["urgent"],
                "sentiment": {
                    "positive": stats["positive"],
                    "negative": stats["negative"],
                    "neutral": stats["neutral"]
                },
                "responses": {
                    "resolved": stats["resolved"],
                    "pending": stats["pending"],
                    "resolution_rate": (stats["resolved"] / stats["total"] * 100) if stats["total"] > 0 else 0
                }
            })
        
        # Sort by total emails descending
        category_breakdown.sort(key=lambda x: x['total_emails'], reverse=True)
        
        return {
            "categories": category_breakdown,
            "total_categories": len(category_breakdown)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving category breakdown: {str(e)}")

@router.get("/performance-metrics")
async def get_performance_metrics():
    """Get AI performance metrics from CSV data"""
    try:
        # Refresh CSV data
        csv_data_service.refresh()
        emails = csv_data_service.get_all()
        
        # Response generation stats
        responses = [e.get('response') for e in emails if e.get('response')]
        total_responses = len(responses)
        high_confidence_responses = sum(1 for r in responses if r.get('confidence_score', 0) >= 0.8)
        
        # Average confidence score
        confidence_scores = [r.get('confidence_score', 0) for r in responses]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Sentiment accuracy (mock data for demo - would need user feedback in real app)
        sentiment_accuracy = 85.2
        
        # Priority accuracy (mock data for demo)
        priority_accuracy = 91.7
        
        # Category accuracy (mock data for demo)
        category_accuracy = 88.3
        
        # Response quality metrics (mock data for demo)
        response_quality = {
            "grammar_score": 96.5,
            "tone_appropriateness": 92.1,
            "relevance_score": 89.4,
            "completeness": 87.8
        }
        
        # Processing speed
        total_emails = len(emails)
        processed_emails = sum(1 for e in emails if e.get('processed', False))
        processing_rate = (processed_emails / total_emails * 100) if total_emails > 0 else 0
        
        return {
            "response_generation": {
                "total_responses": total_responses,
                "high_confidence_responses": high_confidence_responses,
                "avg_confidence_score": round(avg_confidence, 2)
            },
            "accuracy": {
                "sentiment": sentiment_accuracy,
                "priority": priority_accuracy,
                "category": category_accuracy
            },
            "response_quality": response_quality,
            "processing": {
                "total_emails": total_emails,
                "processed_emails": processed_emails,
                "processing_rate": round(processing_rate, 1)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving performance metrics: {str(e)}")
        
        return {
            "response_generation": {
                "total_responses": total_responses,
                "high_confidence_responses": high_confidence_responses,
                "avg_confidence_score": round(avg_confidence, 2),
                "high_confidence_rate": (high_confidence_responses / total_responses * 100) if total_responses > 0 else 0
            },
            "classification_accuracy": {
                "sentiment": sentiment_accuracy,
                "priority": priority_accuracy,
                "category": category_accuracy
            },
            "response_quality": response_quality,
            "processing": {
                "total_emails": total_emails,
                "processed_emails": processed_emails,
                "processing_rate": round(processing_rate, 2)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving performance metrics: {str(e)}")

@router.get("/historical-analytics")
async def get_historical_analytics(days: int = 30):
    """Get historical analytics data from CSV"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Refresh CSV data
        csv_data_service.refresh()
        
        # Get all emails from CSV
        all_emails = csv_data_service.get_all_emails()
        
        # Generate daily stats
        daily_stats = []
        for i in range(days):
            date = end_date - timedelta(days=i)
            date_str = date.isoformat()
            
            # Filter emails for this date
            day_emails = [e for e in all_emails if e.get('received_date', '').startswith(date_str)]
            
            # Count by priority and sentiment
            urgent_count = sum(1 for e in day_emails if e.get('priority') == 'urgent')
            positive_count = sum(1 for e in day_emails if e.get('sentiment') == 'positive')
            negative_count = sum(1 for e in day_emails if e.get('sentiment') == 'negative')
            neutral_count = sum(1 for e in day_emails if e.get('sentiment') == 'neutral')
            
            # Count resolved emails
            resolved_count = sum(1 for e in day_emails if e.get('status') == 'resolved')
            
            daily_stats.append({
                "date": date_str,
                "total_emails": len(day_emails),
                "urgent_emails": urgent_count,
                "positive_sentiment": positive_count,
                "negative_sentiment": negative_count,
                "neutral_sentiment": neutral_count,
                "emails_resolved": resolved_count,
                "emails_pending": len(day_emails) - resolved_count
            })
            
            return {
                "period": f"{days} days",
                "daily_analytics": daily_stats
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving historical analytics: {str(e)}")
