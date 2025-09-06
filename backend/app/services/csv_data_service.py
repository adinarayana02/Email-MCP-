import csv
import json
import os
import logging
from datetime import datetime, timedelta
import pandas as pd
import random

logger = logging.getLogger(__name__)

class CSVDataService:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
        self.csv_path = os.path.join(self.data_dir, 'Support_Emails_Dataset.csv')
        self.dashboard_path = os.path.join(self.data_dir, 'dashboard_data.json')
        self.emails = []
        
    def load(self):
        try:
            if not os.path.exists(self.csv_path):
                logger.error(f"CSV file not found: {self.csv_path}")
                return False
                
            # Load CSV into pandas DataFrame
            df = pd.read_csv(self.csv_path)
            self.emails = df.to_dict('records')
            
            # Process emails
            for email in self.emails:
                # Generate email_id if not present
                if 'email_id' not in email:
                    email['email_id'] = f"{email['sender']}_{email.get('sent_date', '')}"
                
                # Add default fields
                email['status'] = 'pending'
                email['priority'] = self._determine_priority(email)
                email['sentiment'] = self._analyze_sentiment(email)
                
            return True
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            return False
    
    def refresh(self):
        return self.load()
    
    def get_all_emails(self):
        if not self.emails:
            self.load()
        return self.emails
    
    def _determine_priority(self, email):
        subject = email.get('subject', '').lower()
        if "urgent" in subject or "critical" in subject:
            return "urgent"
        elif "important" in subject:
            return "high"
        else:
            return "normal"
    
    def _analyze_sentiment(self, email):
        text = f"{email.get('subject', '')} {email.get('body', '')}".lower()
        positive_words = ["thank", "good", "great"]
        negative_words = ["issue", "problem", "error"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def generate_dashboard_data(self):
        try:
            if not self.emails:
                self.load()
            
            # Basic stats
            total_emails = len(self.emails)
            pending_emails = sum(1 for e in self.emails if e.get('status') == 'pending')
            resolved_emails = sum(1 for e in self.emails if e.get('status') == 'resolved')
            
            # Priority stats
            priority_counts = {'urgent': 0, 'high': 0, 'normal': 0}
            for email in self.emails:
                priority = email.get('priority', 'normal')
                if priority in priority_counts:
                    priority_counts[priority] += 1
            
            # Sentiment stats
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            for email in self.emails:
                sentiment = email.get('sentiment', 'neutral')
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] += 1
            
            # Dashboard data
            dashboard_data = {
                'summary': {
                    'total_emails': total_emails,
                    'pending_emails': pending_emails,
                    'resolved_emails': resolved_emails,
                    'urgent_emails': priority_counts.get('urgent', 0),
                    'avg_response_time': random.randint(30, 120),
                    'ai_accuracy': random.randint(85, 95)
                },
                'charts': {
                    'priority': [
                        {'name': k, 'value': v} for k, v in priority_counts.items() if v > 0
                    ],
                    'sentiment': [
                        {'name': k, 'value': v} for k, v in sentiment_counts.items() if v > 0
                    ]
                }
            }
            
            # Save to JSON
            with open(self.dashboard_path, 'w') as f:
                json.dump(dashboard_data, f)
            
            return dashboard_data
        except Exception as e:
            logger.error(f"Error generating dashboard data: {e}")
            return None