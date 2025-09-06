import sqlite3
import json
import os
import random
import re
from datetime import datetime, timedelta
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from collections import Counter

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')
    nltk.download('punkt')
    nltk.download('stopwords')

# Path to the SQLite database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'email_database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # This enables column access by name
cursor = conn.cursor()

# Categories for emails
CATEGORIES = [
    "account_issue", "billing", "technical_support", 
    "feature_request", "general_inquiry", "bug_report",
    "login_issue", "password_reset", "api_integration", "other"
]

# Priorities for emails
PRIORITIES = ["low", "normal", "high", "urgent"]

# Sentiments for emails
SENTIMENTS = ["negative", "neutral", "positive"]

# Urgent keywords
URGENT_KEYWORDS = [
    "urgent", "immediately", "asap", "emergency", "critical",
    "important", "priority", "urgent matter", "time sensitive",
    "deadline", "cannot access", "locked out", "broken", "down",
    "not working", "error", "failed", "issue", "problem", "help"
]

# Load knowledge base
knowledge_base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'knowledge_base.json')
with open(knowledge_base_path, 'r') as f:
    KNOWLEDGE_BASE = json.load(f)

def create_responses_table():
    # Create responses table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id INTEGER,
        generated_response TEXT,
        confidence_score REAL,
        created_at TIMESTAMP,
        FOREIGN KEY (email_id) REFERENCES emails (id)
    )
    """)
    conn.commit()

def analyze_sentiment(text):
    """Analyze sentiment using NLTK's VADER"""
    sid = SentimentIntensityAnalyzer()
    sentiment_scores = sid.polarity_scores(text)
    compound_score = sentiment_scores['compound']
    
    # Determine sentiment category based on compound score
    if compound_score >= 0.05:
        sentiment = "positive"
    elif compound_score <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "sentiment": sentiment,
        "score": abs(compound_score),  # Use absolute value for score
        "details": sentiment_scores
    }

def determine_priority(subject, body):
    """Determine email priority based on content analysis"""
    text = f"{subject} {body}".lower()
    
    # Check for urgent keywords
    urgency_count = sum(1 for keyword in URGENT_KEYWORDS if keyword in text)
    
    # Check for time-related urgency
    time_urgency = any(phrase in text for phrase in ["today", "tomorrow", "asap", "immediately", "urgent"])
    
    # Check for negative sentiment as it might indicate customer frustration
    sentiment_result = analyze_sentiment(text)
    is_negative = sentiment_result["sentiment"] == "negative"
    
    # Determine priority level
    if urgency_count >= 3 or (time_urgency and is_negative):
        priority = "urgent"
        score = 0.9
    elif urgency_count >= 2 or time_urgency or is_negative:
        priority = "high"
        score = 0.7
    elif urgency_count >= 1:
        priority = "normal"
        score = 0.5
    else:
        priority = "low"
        score = 0.3
    
    return {
        "priority": priority,
        "score": score,
        "urgency_count": urgency_count,
        "time_urgency": time_urgency,
        "is_negative": is_negative
    }

def categorize_email(subject, body):
    """Categorize email based on content analysis"""
    text = f"{subject} {body}".lower()
    
    # Define category keywords
    category_keywords = {
        "account_issue": ["account", "login", "sign in", "password", "reset", "access"],
        "billing": ["bill", "payment", "invoice", "charge", "refund", "subscription", "plan", "price"],
        "technical_support": ["error", "bug", "issue", "problem", "not working", "broken", "fix", "support"],
        "feature_request": ["feature", "add", "suggestion", "improve", "enhancement", "request"],
        "general_inquiry": ["question", "inquiry", "information", "help", "guide", "how to"],
        "bug_report": ["bug", "error", "crash", "issue", "problem", "not working"],
        "login_issue": ["login", "sign in", "cannot access", "password", "authentication"],
        "password_reset": ["password", "reset", "forgot", "change", "recover"],
        "api_integration": ["api", "integration", "endpoint", "request", "response", "documentation"]
    }
    
    # Count keyword matches for each category
    category_scores = {}
    for category, keywords in category_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text)
        category_scores[category] = score
    
    # Find the category with the highest score
    if max(category_scores.values()) > 0:
        best_category = max(category_scores.items(), key=lambda x: x[1])[0]
    else:
        best_category = "other"  # Default category if no keywords match
    
    return best_category

def extract_info(subject, body):
    """Extract structured information from email content"""
    # Extract dates using regex
    date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}'
    dates = re.findall(date_pattern, body)
    
    # Extract emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, body)
    
    # Extract phone numbers
    phone_pattern = r'\+?\d{1,3}?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, body)
    
    # Extract URLs
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, body)
    
    # Extract product names or IDs (simplified)
    product_pattern = r'product[:\s]+([A-Za-z0-9-]+)|model[:\s]+([A-Za-z0-9-]+)'
    products = re.findall(product_pattern, body)
    products = [p[0] or p[1] for p in products if p[0] or p[1]]
    
    # Extract order numbers
    order_pattern = r'order[:\s#]+([A-Za-z0-9-]+)'
    orders = re.findall(order_pattern, body)
    
    # Determine request type based on keywords and categorization
    category = categorize_email(subject, body)
    
    # Extract key phrases using NLTK (simplified)
    tokens = nltk.word_tokenize(body)
    # Get most common words (excluding stopwords)
    stopwords = set(nltk.corpus.stopwords.words('english'))
    words = [word.lower() for word in tokens if word.isalpha() and word.lower() not in stopwords]
    common_words = Counter(words).most_common(5)
    key_phrases = [word for word, count in common_words]
    
    # Get sentiment and priority
    sentiment_result = analyze_sentiment(body)
    priority_result = determine_priority(subject, body)
    
    return {
        "dates": dates,
        "emails": emails,
        "phone_numbers": phones,
        "urls": urls,
        "products": products,
        "orders": orders,
        "category": category,
        "key_phrases": key_phrases,
        "urgency": priority_result["priority"],
        "sentiment": sentiment_result["sentiment"],
        "request_type": category
    }

def generate_response(subject, body, sender, extracted_info, sentiment, priority, category):
    """Generate a context-aware response using the knowledge base"""
    # Get general templates
    greeting = KNOWLEDGE_BASE["general"]["greeting"]
    closing = KNOWLEDGE_BASE["general"]["closing"]
    acknowledgment = KNOWLEDGE_BASE["general"]["acknowledgment"]
    
    # Personalize greeting
    personalized_greeting = f"Dear {sender.split('@')[0]},\n\n{greeting}"
    
    # Get category-specific content if available
    category_content = ""
    if category == "technical_support" and "technical_issues" in KNOWLEDGE_BASE:
        # Check for specific technical issues
        if "login" in body.lower() and "login_problems" in KNOWLEDGE_BASE["technical_issues"]:
            issue_info = KNOWLEDGE_BASE["technical_issues"]["login_problems"]
            category_content = f"\n\n{issue_info['description']}\n"
            for i, solution in enumerate(issue_info["solutions"], 1):
                category_content += f"\n{i}. {solution}"
            category_content += f"\n\n{issue_info['escalation']}"
        
        elif any(word in body.lower() for word in ["slow", "performance", "lag"]) and "performance" in KNOWLEDGE_BASE["technical_issues"]:
            issue_info = KNOWLEDGE_BASE["technical_issues"]["performance"]
            category_content = f"\n\n{issue_info['description']}\n"
            for i, solution in enumerate(issue_info["solutions"], 1):
                category_content += f"\n{i}. {solution}"
            category_content += f"\n\n{issue_info['escalation']}"
        
        elif "bug" in body.lower() and "bugs" in KNOWLEDGE_BASE["technical_issues"]:
            issue_info = KNOWLEDGE_BASE["technical_issues"]["bugs"]
            category_content = f"\n\n{issue_info['description']}\n\nOur process for handling bugs:\n"
            for i, step in enumerate(issue_info["process"], 1):
                category_content += f"\n{i}. {step}"
    
    # If no specific category content, create a generic response
    if not category_content:
        category_content = f"\n\nWe've received your inquiry regarding '{subject}'. "
        if priority == "urgent":
            category_content += "We understand this is an urgent matter and will prioritize our response. "
        category_content += f"Our team is reviewing your request and will provide a detailed response as soon as possible."
    
    # Add sentiment-appropriate content
    sentiment_content = ""
    if sentiment == "negative":
        sentiment_content = "\n\nWe apologize for any inconvenience or frustration this may have caused. We take your concerns seriously and are committed to resolving this matter to your satisfaction."
    elif sentiment == "positive":
        sentiment_content = "\n\nThank you for your positive feedback. We're glad to hear about your experience and will continue to provide the level of service you expect."
    
    # Add priority-appropriate content
    priority_content = ""
    if priority == "urgent":
        priority_content = "\n\nWe understand the urgency of your request and have marked it as high priority. Our team is working to address this immediately."
    
    # Combine all parts
    full_response = f"{personalized_greeting}\n\n{acknowledgment}{category_content}{sentiment_content}{priority_content}\n\n{closing}\n\nBest regards,\nSupport Team"
    
    # Calculate confidence score based on available information
    confidence = 0.7  # Base confidence
    if category_content != "":
        confidence += 0.1  # More confident with category-specific content
    if sentiment_content != "":
        confidence += 0.05  # More confident with sentiment-appropriate content
    if priority_content != "":
        confidence += 0.05  # More confident with priority-appropriate content
    
    return {
        "response": full_response,
        "confidence": min(confidence, 0.95)  # Cap at 0.95
    }

def categorize_email(subject, body, sender):
    """Categorize email based on content"""
    categories = {
        "technical_support": ["error", "bug", "issue", "problem", "not working", "broken", "fix", "crash", "login", "password", "reset", "access"],
        "billing": ["bill", "invoice", "payment", "charge", "refund", "subscription", "plan", "upgrade", "downgrade", "pricing", "cost"],
        "feature_request": ["feature", "request", "suggestion", "improve", "enhancement", "add", "new", "functionality", "capability"],
        "account": ["account", "profile", "settings", "preferences", "delete", "remove", "update", "change", "information"],
        "general_inquiry": ["question", "inquiry", "information", "details", "explain", "clarify", "how to", "guide", "tutorial"],
        "complaint": ["complaint", "dissatisfied", "unhappy", "disappointed", "frustrated", "angry", "upset", "poor", "bad", "terrible"],
        "feedback": ["feedback", "review", "opinion", "thoughts", "experience", "survey", "rating", "stars"],
        "urgent_support": ["urgent", "emergency", "critical", "immediate", "asap", "right away", "quickly", "priority"]
    }
    
    combined_text = f"{subject} {body}".lower()
    category_scores = {}
    
    for category, keywords in categories.items():
        score = sum(1 for keyword in keywords if keyword in combined_text)
        category_scores[category] = score
    
    # Get the category with the highest score
    if max(category_scores.values()) > 0:
        best_category = max(category_scores.items(), key=lambda x: x[1])[0]
    else:
        best_category = "general_inquiry"  # Default category
    
    return best_category

def process_emails():
    # Get all unprocessed emails
    cursor.execute("SELECT * FROM emails WHERE processed = 0")
    unprocessed_emails = cursor.fetchall()
    
    processed_count = 0
    error_count = 0
    
    print(f"Found {len(unprocessed_emails)} unprocessed emails")
    
    # Create a DataFrame for analytics
    analytics_data = {
        "total": len(unprocessed_emails),
        "urgent": 0,
        "high": 0,
        "normal": 0,
        "low": 0,
        "positive": 0,
        "negative": 0,
        "neutral": 0,
        "categories": {}
    }
    
    for email in unprocessed_emails:
        try:
            email_id = email['id']
            subject = email['subject']
            body = email['body']
            sender = email['sender']
            
            print(f"Processing email {email_id}: {subject}")
            
            # Analyze sentiment
            sentiment_result = analyze_sentiment(f"{subject} {body}")
            sentiment = sentiment_result["sentiment"]
            sentiment_score = sentiment_result["score"]
            
            # Determine priority
            priority_result = determine_priority(subject, body)
            priority = priority_result["priority"]
            priority_score = priority_result["score"]
            
            # Categorize email
            category = categorize_email(subject, body, sender)
            
            # Extract information
            extracted_info = extract_info(subject, body)
            
            # Generate a context-aware response
            response_result = generate_response(subject, body, sender, extracted_info, sentiment, priority, category)
            generated_response = response_result["response"]
            confidence = response_result["confidence"]
            
            # Update email record
            cursor.execute("""
            UPDATE emails SET 
                sentiment = ?,
                sentiment_score = ?,
                priority = ?,
                priority_score = ?,
                category = ?,
                extracted_info = ?,
                processed = 1,
                status = ?
            WHERE id = ?
            """, (
                sentiment,
                sentiment_score,
                priority,
                priority_score,
                category,
                json.dumps(extracted_info),
                "pending" if priority == "urgent" else "in_progress",
                email_id
            ))
            
            # Save response
            cursor.execute("""
            INSERT INTO responses (email_id, generated_response, confidence_score, created_at)
            VALUES (?, ?, ?, ?)
            """, (
                email_id,
                generated_response,
                confidence,
                datetime.now().isoformat()
            ))
            
            # Update analytics
            analytics_data[priority] = analytics_data.get(priority, 0) + 1
            analytics_data[sentiment] = analytics_data.get(sentiment, 0) + 1
            analytics_data["categories"][category] = analytics_data["categories"].get(category, 0) + 1
            
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing email {email['id']}: {e}")
            error_count += 1
            continue
    
    # Update analytics table
    try:
        # Get today's date
        today = datetime.now().date()
        
        # Check if we already have an analytics record for today
        cursor.execute("SELECT id FROM analytics WHERE date(date) = date(?)", (today.isoformat(),))
        analytics_record = cursor.fetchone()
        
        if analytics_record:
            # Update existing record
            cursor.execute("""
            UPDATE analytics SET 
                total_emails = total_emails + ?,
                urgent_emails = urgent_emails + ?,
                high_priority_emails = high_priority_emails + ?,
                positive_sentiment = positive_sentiment + ?,
                negative_sentiment = negative_sentiment + ?,
                neutral_sentiment = neutral_sentiment + ?
            WHERE id = ?
            """, (
                processed_count,
                analytics_data.get("urgent", 0),
                analytics_data.get("high", 0),
                analytics_data.get("positive", 0),
                analytics_data.get("negative", 0),
                analytics_data.get("neutral", 0),
                analytics_record[0]
            ))
        else:
            # Create new record
            cursor.execute("""
            INSERT INTO analytics (
                date, total_emails, urgent_emails, high_priority_emails,
                positive_sentiment, negative_sentiment, neutral_sentiment
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                today.isoformat(),
                processed_count,
                analytics_data.get("urgent", 0),
                analytics_data.get("high", 0),
                analytics_data.get("positive", 0),
                analytics_data.get("negative", 0),
                analytics_data.get("neutral", 0)
            ))
    except Exception as e:
        print(f"Error updating analytics: {e}")
    
    # Commit changes
    conn.commit()
    print(f"Successfully processed {processed_count} emails, {error_count} errors")
    return {
        "processed": processed_count, 
        "errors": error_count,
        "analytics": analytics_data
    }

def create_analytics_table():
    # Create analytics table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TIMESTAMP,
        total_emails INTEGER DEFAULT 0,
        urgent_emails INTEGER DEFAULT 0,
        high_priority_emails INTEGER DEFAULT 0,
        positive_sentiment INTEGER DEFAULT 0,
        negative_sentiment INTEGER DEFAULT 0,
        neutral_sentiment INTEGER DEFAULT 0,
        emails_resolved INTEGER DEFAULT 0,
        emails_pending INTEGER DEFAULT 0,
        emails_in_progress INTEGER DEFAULT 0,
        avg_response_time REAL DEFAULT 0.0,
        satisfaction_score REAL DEFAULT 0.0
    )
    """)
    conn.commit()

def update_dashboard_data():
    """Generate dashboard data for the frontend"""
    # Get email statistics
    cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN processed = 1 THEN 1 ELSE 0 END) as processed,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
        SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
        SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved,
        SUM(CASE WHEN priority = 'urgent' THEN 1 ELSE 0 END) as urgent,
        SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high,
        SUM(CASE WHEN priority = 'normal' THEN 1 ELSE 0 END) as normal,
        SUM(CASE WHEN priority = 'low' THEN 1 ELSE 0 END) as low,
        SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive,
        SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative,
        SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral,
        COUNT(DISTINCT category) as category_count
    FROM emails
    """)
    email_stats = cursor.fetchone()
    
    # Get category distribution with percentage
    cursor.execute("""
    SELECT category, COUNT(*) as count
    FROM emails
    WHERE category IS NOT NULL
    GROUP BY category
    ORDER BY count DESC
    """)
    category_rows = cursor.fetchall()
    total_categorized = sum(row[1] for row in category_rows)
    categories = {}
    for row in category_rows:
        categories[row[0]] = {
            "count": row[1],
            "percentage": round((row[1] / total_categorized * 100) if total_categorized > 0 else 0, 2)
        }
    
    # Get recent emails for dashboard with extracted info
    cursor.execute("""
    SELECT e.id, e.sender, e.subject, e.received_date, e.priority, e.sentiment, e.status, r.generated_response, e.extracted_info, e.category, e.body
    FROM emails e
    LEFT JOIN responses r ON e.id = r.email_id
    ORDER BY e.received_date DESC
    LIMIT 10
    """)
    recent_emails = []
    for row in cursor.fetchall():
        email_data = {
            "id": row[0],
            "sender": row[1],
            "subject": row[2],
            "received_date": row[3],
            "priority": row[4],
            "sentiment": row[5],
            "status": row[6],
            "response": row[7],
            "category": row[9],
            "preview": row[10][:100] + "..." if row[10] and len(row[10]) > 100 else row[10]
        }
        
        # Add extracted info if available
        if row[8]:
            try:
                extracted = json.loads(row[8])
                email_data["extracted_info"] = extracted
            except:
                email_data["extracted_info"] = {}
        
        recent_emails.append(email_data)
    
    # Get daily email volume for the past week
    cursor.execute("""
    SELECT date(received_date) as day, COUNT(*) as count
    FROM emails
    WHERE received_date >= date('now', '-7 days')
    GROUP BY day
    ORDER BY day
    """)
    daily_volume = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Get information extraction data
    cursor.execute("""
    SELECT id, extracted_info
    FROM emails
    WHERE extracted_info IS NOT NULL
    ORDER BY received_date DESC
    LIMIT 20
    """)
    extracted_info_data = {}
    for row in cursor.fetchall():
        if row[1]:
            try:
                extracted_info_data[row[0]] = json.loads(row[1])
            except:
                extracted_info_data[row[0]] = row[1]
    
    # Get response time metrics
    cursor.execute("""
    SELECT AVG(response_time_minutes) as avg_response_time
    FROM emails
    WHERE response_time_minutes IS NOT NULL
    """)
    avg_response_time = cursor.fetchone()[0] or 0
    
    # Get sentiment distribution with percentage
    cursor.execute("""
    SELECT sentiment, COUNT(*) as count
    FROM emails
    WHERE sentiment IS NOT NULL
    GROUP BY sentiment
    ORDER BY count DESC
    """)
    sentiment_rows = cursor.fetchall()
    total_sentiment = sum(row[1] for row in sentiment_rows)
    sentiment_distribution = {}
    for row in sentiment_rows:
        sentiment_distribution[row[0]] = {
            "count": row[1],
            "percentage": round((row[1] / total_sentiment * 100) if total_sentiment > 0 else 0, 2)
        }
    
    # Get priority distribution with percentage
    cursor.execute("""
    SELECT priority, COUNT(*) as count
    FROM emails
    WHERE priority IS NOT NULL
    GROUP BY priority
    ORDER BY count DESC
    """)
    priority_rows = cursor.fetchall()
    total_priority = sum(row[1] for row in priority_rows)
    priority_distribution = {}
    for row in priority_rows:
        priority_distribution[row[0]] = {
            "count": row[1],
            "percentage": round((row[1] / total_priority * 100) if total_priority > 0 else 0, 2)
        }
    
    # Prepare dashboard data
    dashboard_data = {
        "email_stats": dict(email_stats),
        "categories": categories,
        "sentiment_distribution": sentiment_distribution,
        "priority_distribution": priority_distribution,
        "recent_emails": recent_emails,
        "daily_volume": daily_volume,
        "extracted_info": extracted_info_data,
        "metrics": {
            "avg_response_time": avg_response_time,
            "satisfaction_score": 4.2,  # Mock data for demo
            "response_rate": round((email_stats['resolved'] / email_stats['total'] * 100) if email_stats['total'] > 0 else 0, 2),
            "urgent_handling_rate": round((email_stats['urgent'] / email_stats['total'] * 100) if email_stats['total'] > 0 else 0, 2)
        }
    }
    
    # Ensure data directory exists
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save dashboard data to a file for the frontend
    dashboard_path = os.path.join(data_dir, 'dashboard_data.json')
    with open(dashboard_path, 'w') as f:
        json.dump(dashboard_data, f, indent=2, default=str)
    
    return dashboard_data

if __name__ == "__main__":
    import re  # Import re module for regex patterns
    create_responses_table()
    create_analytics_table()
    result = process_emails()
    dashboard_data = update_dashboard_data()
    print(json.dumps(result, indent=2, default=str))
    print("\nDashboard data updated.")
    conn.close()