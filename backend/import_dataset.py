import csv
import json
import os
from datetime import datetime
from hashlib import md5
import sqlite3

# Path to the dataset
dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'Support_Emails_Dataset.csv')

# Path to the SQLite database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'email_database.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id TEXT UNIQUE,
    sender TEXT,
    subject TEXT,
    body TEXT,
    received_date TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    sentiment TEXT,
    sentiment_score REAL,
    priority TEXT,
    priority_score REAL,
    category TEXT,
    extracted_info TEXT,
    status TEXT DEFAULT 'pending',
    assigned_to TEXT,
    response_time_minutes INTEGER,
    thread_id TEXT,
    metadata TEXT
)
""")

# Function to clean email text
def clean_email_text(text):
    if not text:
        return ""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    return text

# Import emails from CSV
def import_emails():
    imported = 0
    skipped = 0
    
    try:
        with open(dataset_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Extract basic fields
                sender = row.get('sender') or row.get('from') or row.get('email')
                subject = row.get('subject')
                body = row.get('body')
                date_val = row.get('sent_date') or row.get('date')
                
                # Skip if missing essential fields
                if not sender or not subject:
                    skipped += 1
                    continue
                
                # Parse date
                received_date = None
                if date_val:
                    # Try several formats
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M", "%d-%b-%Y", "%d/%m/%Y", "%m/%d/%Y"):
                        try:
                            received_date = datetime.strptime(str(date_val), fmt)
                            break
                        except Exception:
                            continue
                if not received_date:
                    received_date = datetime.now()
                
                # Clean body text
                cleaned_body = clean_email_text(str(body or ""))
                
                # Deterministic email_id based on sender+subject+date
                key = f"{sender}|{subject}|{received_date.isoformat()}"
                email_id = md5(key.encode('utf-8')).hexdigest()
                
                # Check if email already exists
                cursor.execute("SELECT id FROM emails WHERE email_id = ?", (email_id,))
                if cursor.fetchone():
                    skipped += 1
                    continue
                
                # Insert email into database
                cursor.execute("""
                INSERT INTO emails 
                (email_id, sender, subject, body, received_date, processed, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    email_id,
                    str(sender),
                    str(subject),
                    cleaned_body,
                    received_date.isoformat(),
                    False,
                    'pending'
                ))
                
                imported += 1
        
        # Commit changes
        conn.commit()
        print(f"Successfully imported {imported} emails, skipped {skipped} duplicates.")
        return {"imported": imported, "skipped": skipped}
    
    except Exception as e:
        conn.rollback()
        print(f"Error importing emails: {e}")
        return {"imported": 0, "skipped": 0, "error": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    result = import_emails()
    print(json.dumps(result, indent=2))