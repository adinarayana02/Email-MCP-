import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime, timedelta
import re
from typing import List, Dict, Tuple
import logging
from sqlalchemy.orm import Session
import csv
from hashlib import md5
from datetime import datetime
from typing import Optional

from app.config import settings
from app.database import Email, get_db
from app.utils.email_utils import EmailUtils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        pass
    
    def _normalize_path(self, path: str) -> str:
        if not path:
            return path
        p = str(path).strip()
        if (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
            p = p[1:-1]
        return p
        
    def connect_imap(self) -> imaplib.IMAP4_SSL:
        """Connect to IMAP server"""
        try:
            mail = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
            mail.login(settings.imap_username, settings.imap_password)
            return mail
        except Exception as e:
            logger.error(f"Failed to connect to IMAP: {e}")
            raise

    def fetch_emails(self, days_back: int = 1, max_emails: int = 100, 
                    filters: Optional[Dict] = None, 
                    folders: Optional[List[str]] = None) -> List[Dict]:
        """Fetch emails with advanced filtering options
        
        Args:
            days_back (int): Number of days to look back for emails
            max_emails (int): Maximum number of emails to retrieve
            filters (Dict, optional): Additional filtering criteria like priority, sender domain, etc.
            folders (List[str], optional): Email folders to search in (defaults to INBOX)
            
        Returns:
            List[Dict]: List of email data dictionaries
        """
        try:
            mail = self.connect_imap()
            
            # Select folders to search in
            search_folders = folders if folders else ['INBOX']
            all_emails = []
            
            for folder in search_folders:
                try:
                    status, _ = mail.select(folder)
                    if status != 'OK':
                        logger.warning(f"Could not select folder {folder}, skipping")
                        continue
                        
                    # Calculate date for filtering
                    date_filter = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
                    
                    # Build search query components
                    query_components = [f'(SINCE "{date_filter}")']  # Base date filter
                    
                    # Process custom filters
                    if filters:
                        # Filter by sender domain if specified
                        if 'sender_domain' in filters and filters['sender_domain']:
                            domains = filters['sender_domain'] if isinstance(filters['sender_domain'], list) else [filters['sender_domain']]
                            domain_queries = [f'(FROM "*@{domain}")' for domain in domains]
                            if domain_queries:
                                query_components.append(f"({' OR '.join(domain_queries)})")
                        
                        # Filter by subject keywords if specified
                        if 'subject_keywords' in filters and filters['subject_keywords']:
                            keywords = filters['subject_keywords'] if isinstance(filters['subject_keywords'], list) else [filters['subject_keywords']]
                            subject_queries = [f'(SUBJECT "{keyword}")' for keyword in keywords]
                            if subject_queries:
                                query_components.append(f"({' OR '.join(subject_queries)})")
                        
                        # Filter by flagged/important status
                        if 'flagged' in filters and filters['flagged']:
                            query_components.append('(FLAGGED)')
                        
                        # Filter by unread status
                        if 'unread' in filters and filters['unread']:
                            query_components.append('(UNSEEN)')
                    
                    # Add support-related keyword filtering if no specific subject keywords provided
                    if not (filters and 'subject_keywords' in filters and filters['subject_keywords']):
                        # Search both subject and body for support-related keywords
                        subject_query = ' OR '.join([f'SUBJECT "{keyword}"' for keyword in settings.support_keywords])
                        # Add additional search criteria for common support indicators in the body
                        body_terms = ['issue', 'problem', 'help', 'support', 'error', 'not working', 'broken', 'failed', 'bug', 'question']
                        body_query = ' OR '.join([f'BODY "{term}"' for term in body_terms])
                        query_components.append(f"(({subject_query}) OR ({body_query}))")
                    
                    # Combine all query components
                    search_query = ' '.join(query_components)
                    
                    logger.info(f"Executing email search in folder {folder} with query: {search_query}")
                    status, message_ids = mail.search(None, search_query)
                    
                    if status != 'OK' or not message_ids[0]:
                        logger.warning(f"No emails found matching criteria in folder {folder}")
                        continue
                    
                    message_ids = message_ids[0].split()
                    total_messages = len(message_ids)
                    
                    logger.info(f"Found {total_messages} potential emails in folder {folder}")
                    
                    # Process the most recent emails first, limited by max_emails
                    # Calculate how many emails to fetch from this folder based on remaining quota
                    remaining_quota = max_emails - len(all_emails)
                    if remaining_quota <= 0:
                        break
                        
                    folder_limit = min(remaining_quota, total_messages)
                    for msg_id in reversed(message_ids[-folder_limit:]):
                        try:
                            # Fetch email with headers and flags for more complete metadata
                            status, msg_data = mail.fetch(msg_id, '(RFC822 FLAGS)')
                            if status == 'OK':
                                email_body = msg_data[0][1]
                                email_message = email.message_from_bytes(email_body)
                                
                                # Get flags if available
                                flags = []
                                for item in msg_data:
                                    if isinstance(item, tuple) and b'FLAGS' in item[0]:
                                        flags_match = re.search(rb'\(FLAGS \(([^)]+)\)\)', item[0])
                                        if flags_match:
                                            flags = flags_match.group(1).decode().split()
                                
                                # Extract email details with more robust parsing
                                email_data = self._parse_email(email_message, msg_id.decode())
                                if email_data:
                                    # Add folder and flags information
                                    email_data['folder'] = folder
                                    email_data['flags'] = flags
                                    all_emails.append(email_data)
                                    logger.debug(f"Added email from {folder}: {email_data['subject']}")
                            else:
                                logger.warning(f"Failed to fetch email {msg_id} from {folder}: Status {status}")
                                    
                        except Exception as e:
                            logger.error(f"Error parsing email {msg_id} from {folder}: {str(e)}")
                            continue
                except Exception as folder_error:
                    logger.error(f"Error processing folder {folder}: {str(folder_error)}")
                    continue
                    
                # Check if we've reached the maximum emails limit
                if len(all_emails) >= max_emails:
                    break
            
            mail.close()
            mail.logout()
            
            logger.info(f"Successfully processed {len(all_emails)} emails from {len(search_folders)} folders")
            return all_emails
            
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error while fetching emails: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching emails: {str(e)}")
            return []

    def _parse_email(self, email_message, email_id: str) -> Dict:
        """Parse email message and extract relevant information with enhanced metadata
        
        Args:
            email_message: The email message object
            email_id: Unique identifier for the email
            
        Returns:
            Dict containing parsed email data or None if parsing fails
        """
        try:
            # Extract basic email fields with fallbacks for missing headers
            sender = email_message.get('From', '')
            subject = email_message.get('Subject', '') or ''
            # Decode subject if needed
            if subject and hasattr(email.header, 'decode_header'):
                decoded_chunks = []
                for chunk, encoding in email.header.decode_header(subject):
                    if isinstance(chunk, bytes):
                        try:
                            if encoding:
                                decoded_chunks.append(chunk.decode(encoding))
                            else:
                                decoded_chunks.append(chunk.decode('utf-8', errors='replace'))
                        except Exception:
                            # Fallback to utf-8 with replacement if decoding fails
                            decoded_chunks.append(chunk.decode('utf-8', errors='replace'))
                    else:
                        decoded_chunks.append(chunk)
                subject = ''.join(decoded_chunks)
            
            # Extract and parse date with robust format handling
            date_str = email_message.get('Date', '')
            received_date = self._parse_email_date(date_str)
            
            # Extract all relevant headers
            cc = email_message.get('Cc', '')
            bcc = email_message.get('Bcc', '')
            reply_to = email_message.get('Reply-To', '')
            message_id = email_message.get('Message-ID', '')
            in_reply_to = email_message.get('In-Reply-To', '')
            references = email_message.get('References', '')
            thread_id = email_message.get('Thread-Index', '') or references or in_reply_to
            importance = email_message.get('Importance', 'normal')
            priority_header = email_message.get('X-Priority', '') or email_message.get('Priority', '')
            
            # Extract sender details (name and email)
            sender_name, sender_email = self._extract_sender_details(sender)
            
            # Extract email body with better handling of multipart messages
            body, has_attachments, attachment_info = self._extract_body_and_attachments(email_message)
            
            # Check if email is support-related
            # First check subject, then body if subject doesn't match
            is_support_email = self._contains_support_keywords(subject.lower())
            if not is_support_email and body:
                is_support_email = self._contains_support_keywords(body.lower())
                
            # Skip non-support emails if configured to filter them
            # But allow override with explicit filters
            if not is_support_email and not getattr(settings, 'include_all_emails', False):
                return None
            
            # Extract additional metadata
            metadata = {
                'cc': cc,
                'bcc': bcc,
                'reply_to': reply_to,
                'message_id': message_id,
                'in_reply_to': in_reply_to,
                'references': references,
                'thread_id': thread_id,
                'importance': importance,
                'priority_header': priority_header,
                'has_attachments': has_attachments,
                'attachment_count': len(attachment_info) if attachment_info else 0,
                'attachment_info': attachment_info
            }
            
            # Determine preliminary priority based on multiple signals
            priority = self._determine_preliminary_priority(subject, importance, priority_header)
            
            # Extract domain from sender email
            domain = sender_email.split('@')[1] if '@' in sender_email else ''
            
            return {
                'email_id': email_id,
                'sender': sender,
                'sender_name': sender_name,
                'sender_email': sender_email,
                'sender_domain': domain,
                'subject': subject,
                'body': body,
                'received_date': received_date,
                'metadata': metadata,
                'preliminary_priority': priority,
                'has_attachments': has_attachments
            }
            
        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            return None
            
    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date with support for multiple formats"""
        if not date_str:
            return datetime.now()
            
        # List of common date formats in emails
        date_formats = [
            '%a, %d %b %Y %H:%M:%S %z',  # RFC 2822 format with timezone
            '%a, %d %b %Y %H:%M:%S %Z',  # RFC 2822 format with timezone name
            '%d %b %Y %H:%M:%S %z',      # Alternate format with timezone
            '%a, %d %b %Y %H:%M:%S',     # Without timezone
            '%d %b %Y %H:%M:%S',         # Simple format
            '%a, %d %b %Y %H:%M',        # Without seconds
            '%Y-%m-%dT%H:%M:%S%z',       # ISO format
            '%Y-%m-%dT%H:%M:%S',         # ISO format without timezone
        ]
        
        # Try each format
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # Remove timezone info for SQLite compatibility if present
                if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return dt
            except ValueError:
                continue
                
        # If all parsing attempts fail, try email.utils parser
        try:
            import email.utils
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            if parsed_date:
                return parsed_date.replace(tzinfo=None)
        except Exception:
            pass
            
        # Default to current time if all parsing fails
        logger.warning(f"Could not parse date: {date_str}, using current time")
        return datetime.now()
        
    def _extract_sender_details(self, sender: str) -> Tuple[str, str]:
        """Extract sender name and email address from From header"""
        if not sender:
            return '', ''
            
        # Try email.utils parser first
        try:
            import email.utils
            parsed = email.utils.parseaddr(sender)
            if parsed and len(parsed) == 2:
                return parsed[0], parsed[1]
        except Exception:
            pass
            
        # Fallback to regex parsing
        try:
            # Pattern for "Name <email@example.com>" format
            match = re.search(r'([^<]+)<([^>]+)>', sender)
            if match:
                return match.group(1).strip(), match.group(2).strip()
                
            # If no match, check if it's just an email address
            if '@' in sender:
                return '', sender.strip()
        except Exception:
            pass
            
        # If all parsing fails, return original as email and empty name
        return '', sender.strip()
        
    def _determine_preliminary_priority(self, subject: str, importance: str, priority_header: str) -> str:
        """Determine preliminary priority based on email headers and subject"""
        # Default priority
        priority = 'normal'
        
        # Check importance header
        if importance and importance.lower() in ['high', 'urgent']:
            priority = 'urgent'
            
        # Check X-Priority header (1 is highest)
        if priority_header:
            try:
                # Some clients use numeric values
                if priority_header.strip() in ['1', '2']:
                    priority = 'urgent'
                elif priority_header.lower() in ['urgent', 'high']:
                    priority = 'urgent'
            except Exception:
                pass
                
        # Check subject for urgent keywords
        urgent_terms = ['urgent', 'critical', 'emergency', 'immediate', 'asap', 'important', 'priority', 'attention']
        if any(urgent_term in subject.lower() for urgent_term in urgent_terms):
            priority = 'urgent'
            
        return priority

    def _extract_body_and_attachments(self, email_message) -> Tuple[str, bool, List[Dict]]:
        """Extract the body text and attachment information from an email message
        
        Args:
            email_message: The email message object
            
        Returns:
            Tuple containing:
            - body text (str)
            - has_attachments flag (bool)
            - list of attachment info dictionaries
        """
        body = ""
        has_attachments = False
        attachment_info = []
        plain_text_body = ""
        html_body = ""
        
        # Process each part of the email
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition") or '')
                filename = part.get_filename()
                
                # Handle attachments
                if "attachment" in content_disposition or filename:
                    has_attachments = True
                    try:
                        size = len(part.get_payload(decode=True) or b'')
                        attachment_info.append({
                            'filename': filename or 'unnamed_attachment',
                            'content_type': content_type,
                            'size': size,
                            'content_id': part.get('Content-ID', '')
                        })
                    except Exception as e:
                        logger.warning(f"Error processing attachment: {str(e)}")
                    continue
                
                # Get text content
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        payload = part.get_payload(decode=True)
                        if payload:
                            plain_text_body += payload.decode(charset, errors='replace')
                    except Exception as e:
                        logger.error(f"Error extracting email body: {str(e)}")
                        # Try without decoding
                        try:
                            plain_text_body += part.get_payload()
                        except:
                            pass
                            
                # Get HTML content
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        payload = part.get_payload(decode=True)
                        if payload:
                            html_body += payload.decode(charset, errors='replace')
                    except Exception as e:
                        logger.error(f"Error extracting HTML email body: {str(e)}")
        else:
            # Not multipart - get the content directly
            content_type = email_message.get_content_type()
            filename = email_message.get_filename()
            
            # Check if it's an attachment
            if filename or email_message.get("Content-Disposition", "").startswith("attachment"):
                has_attachments = True
                try:
                    size = len(email_message.get_payload(decode=True) or b'')
                    attachment_info.append({
                        'filename': filename or 'unnamed_attachment',
                        'content_type': content_type,
                        'size': size,
                        'content_id': email_message.get('Content-ID', '')
                    })
                except Exception as e:
                    logger.warning(f"Error processing attachment: {str(e)}")
            else:
                try:
                    if content_type == "text/plain":
                        charset = email_message.get_content_charset() or 'utf-8'
                        payload = email_message.get_payload(decode=True)
                        if payload:
                            plain_text_body = payload.decode(charset, errors='replace')
                    elif content_type == "text/html":
                        charset = email_message.get_content_charset() or 'utf-8'
                        payload = email_message.get_payload(decode=True)
                        if payload:
                            html_body = payload.decode(charset, errors='replace')
                except Exception as e:
                    logger.error(f"Error extracting email body: {str(e)}")
                    # Try without decoding
                    try:
                        if content_type == "text/plain":
                            plain_text_body = email_message.get_payload()
                        elif content_type == "text/html":
                            html_body = email_message.get_payload()
                    except:
                        pass
        
        # Prioritize plain text over HTML if available
        if plain_text_body:
            body = plain_text_body
        elif html_body:
            body = self._html_to_text(html_body)
        
        # Clean the body text
        body = EmailUtils.clean_email_text(body)
        return body, has_attachments, attachment_info
        
    def _extract_body(self, email_message) -> str:
        """Legacy method for backward compatibility"""
        body, _, _ = self._extract_body_and_attachments(email_message)
        return body

    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML content to plain text
        
        Args:
            html_content: HTML content to convert
            
        Returns:
            Plain text extracted from HTML
        """
        try:
            # Try using BeautifulSoup if available
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            # Get text and handle whitespace
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except ImportError:
            # Fallback to regex-based extraction if BeautifulSoup is not available
            import re
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html_content)
            
            # Replace common HTML entities
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&amp;', '&')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&quot;', '"')
            text = text.replace('&#39;', "'")
            
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error converting HTML to text: {str(e)}")
            # Last resort: strip all HTML tags with minimal processing
            import re
            return re.sub(r'<[^>]*>', '', html_content)
    
    def _contains_support_keywords(self, text: str) -> bool:
        """Check if text contains support-related keywords with more sophisticated matching"""
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Direct keyword matching
        if any(keyword.lower() in text_lower for keyword in settings.support_keywords):
            return True
            
        # Check for variations of support keywords (e.g., "supporting", "supported")
        support_stems = ["support", "help", "assist", "query", "request", "issue", "problem", "trouble"]
        if any(stem in text_lower for stem in support_stems):
            return True
            
        # Check for common support phrases
        support_phrases = [
            "not working", "doesn't work", "having trouble", "need assistance",
            "how do i", "how to", "can you help", "please help", "urgent help",
            "technical issue", "bug report", "feature request", "account problem"
        ]
        if any(phrase in text_lower for phrase in support_phrases):
            return True
            
        return False

    def save_emails_to_db(self, emails: List[Dict], db: Session):
        """Save emails to database with enhanced metadata"""
        saved_count = 0
        
        for email_data in emails:
            try:
                # Check if email already exists
                existing_email = db.query(Email).filter(
                    Email.email_id == email_data['email_id']
                ).first()
                
                if not existing_email:
                    # Extract metadata if available
                    metadata = email_data.get('metadata', {})
                    thread_id = metadata.get('thread_id', '') if metadata else ''
                    
                    # Get preliminary priority if available
                    priority = email_data.get('preliminary_priority', 'normal')
                    priority_score = 0.7 if priority == 'urgent' else 0.5
                    
                    # Create new email record with enhanced data
                    db_email = Email(
                        email_id=email_data['email_id'],
                        sender=email_data['sender'],
                        subject=email_data['subject'],
                        body=email_data['body'],
                        received_date=email_data['received_date'],
                        thread_id=thread_id,
                        priority=priority,
                        priority_score=priority_score,
                        # Store metadata as JSON string
                        extracted_info=json.dumps(metadata) if metadata else None
                    )
                    db.add(db_email)
                    saved_count += 1
                    logger.debug(f"Added new email: {email_data['subject']}")
                    
            except Exception as e:
                logger.error(f"Error saving email to DB: {str(e)}")
                continue
        
        try:
            if saved_count > 0:
                db.commit()
                logger.info(f"Saved {saved_count} new emails to database")
            return saved_count
        except Exception as e:
            db.rollback()
            logger.error(f"Error committing emails to database: {str(e)}")
            return 0

    def load_emails_from_dataset(self) -> List[Dict]:
        """Load emails directly from configured dataset without DB for dataset mode with enhanced metadata."""
        path = self._normalize_path(settings.dataset_path or "./Support_Emails_Dataset.csv")
        try:
            results: List[Dict] = []
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Extract basic fields
                    sender = row.get('sender') or row.get('from') or row.get('email')
                    subject = row.get('subject')
                    body = row.get('body')
                    date_val = row.get('sent_date') or row.get('date')
                    category = row.get('category')
                    thread_id = row.get('thread_id')
                    priority = row.get('priority')
                    
                    # Skip if missing essential fields
                    if not sender or not subject:
                        continue
                        
                    # Check if this is a support email
                    is_support_email = self._contains_support_keywords(str(subject).lower())
                    if not is_support_email and body:
                        is_support_email = self._contains_support_keywords(str(body).lower())
                    if not is_support_email:
                        continue
                        
                    # Parse date
                    try:
                        received_date = datetime.fromisoformat(str(date_val)) if date_val else datetime.now()
                    except Exception:
                        received_date = datetime.now()
                        
                    # Generate unique ID
                    key = f"{sender}|{subject}|{received_date.isoformat()}"
                    email_id = md5(key.encode('utf-8')).hexdigest()
                    
                    # Determine priority if not provided
                    if not priority:
                        priority = 'urgent' if any(urgent_term in subject.lower() 
                                                for urgent_term in ['urgent', 'critical', 'emergency', 'immediate', 'asap']) \
                                    else 'normal'
                    
                    # Create metadata dictionary
                    metadata = {
                        'thread_id': thread_id or '',
                        'category': category or '',
                        'cc': row.get('cc', ''),
                        'reply_to': row.get('reply_to', ''),
                        'importance': 'high' if priority == 'urgent' else 'normal'
                    }
                    results.append({
                        'email_id': email_id,
                        'sender': sender,
                        'subject': subject,
                        'body': EmailUtils.clean_email_text(str(body or "")),
                        'received_date': received_date,
                        'metadata': metadata,
                        'preliminary_priority': priority
                    })
            return results
        except Exception as e:
            logger.error(f"Failed to load dataset emails: {e}")
            return []

    def import_emails_from_file(self, file_path: str, db: Session, file_type: Optional[str] = None) -> Dict:
        """Import emails from a CSV or Excel file and save to DB.

        The file is expected to contain columns for sender, subject, body, and an optional date.
        This method attempts to infer common column names.
        """
        try:
            file_type_lower = (file_type or '').lower()
            if not file_type_lower:
                if file_path.lower().endswith('.csv'):
                    file_type_lower = 'csv'
                elif file_path.lower().endswith(('.xls', '.xlsx')):
                    file_type_lower = 'excel'
                else:
                    file_type_lower = 'csv'  # default

            rows: List[Dict] = []

            if file_type_lower == 'csv':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        rows.append(row)
            elif file_type_lower == 'excel':
                try:
                    import pandas as pd  # optional dependency
                    df = pd.read_excel(file_path)
                    rows = df.to_dict(orient='records')
                except Exception as e:
                    logger.error(f"Failed to read Excel file, ensure pandas/openpyxl are installed: {e}")
                    return {"imported": 0, "skipped": 0, "error": "Excel read failed"}
            else:
                return {"imported": 0, "skipped": 0, "error": f"Unsupported file type: {file_type_lower}"}

            imported: List[Dict] = []
            skipped = 0

            # Common column name candidates
            sender_keys = ['sender', 'from', 'email', 'from_email', 'sender_email']
            subject_keys = ['subject', 'title']
            body_keys = ['body', 'message', 'content', 'email_body']
            date_keys = ['received_date', 'date', 'time', 'timestamp']

            for r in rows:
                # Normalize keys to lowercase for lookup
                norm = {str(k).strip().lower(): v for k, v in r.items()}
                sender = next((norm[k] for k in sender_keys if k in norm and norm[k]), None)
                subject = next((norm[k] for k in subject_keys if k in norm and norm[k]), None)
                body = next((norm[k] for k in body_keys if k in norm and norm[k]), None)
                date_val = next((norm[k] for k in date_keys if k in norm and norm[k]), None)

                if not subject or not sender:
                    skipped += 1
                    continue

                # Filter by support keywords in subject
                if not self._contains_support_keywords(str(subject).lower()):
                    continue

                # Parse date
                received_date = None
                if date_val:
                    try:
                        # Try several formats
                        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M", "%d-%b-%Y", "%d/%m/%Y", "%m/%d/%Y"):
                            try:
                                received_date = datetime.strptime(str(date_val), fmt)
                                break
                            except Exception:
                                continue
                    except Exception:
                        received_date = None
                if not received_date:
                    received_date = datetime.now()

                # Clean body text
                cleaned_body = EmailUtils.clean_email_text(str(body or ""))

                # Deterministic email_id based on sender+subject+date
                key = f"{sender}|{subject}|{received_date.isoformat()}"
                email_id = md5(key.encode('utf-8')).hexdigest()

                imported.append({
                    'email_id': email_id,
                    'sender': str(sender),
                    'subject': str(subject),
                    'body': cleaned_body,
                    'received_date': received_date,
                })

            saved = self.save_emails_to_db(imported, db)
            return {"imported": saved, "skipped": skipped, "total_rows": len(rows)}
        except Exception as e:
            logger.error(f"Error importing emails from file: {e}")
            return {"imported": 0, "skipped": 0, "error": str(e)}

    def send_response(self, to_email: str, subject: str, response_body: str) -> bool:
        """Send email response"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.email_username
            msg['To'] = to_email
            msg['Subject'] = f"Re: {subject}"
            
            msg.attach(MIMEText(response_body, 'plain'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(settings.email_username, settings.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Response sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending response: {e}")
            return False