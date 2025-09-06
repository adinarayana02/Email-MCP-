import re
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class EmailUtils:
    """Utility functions for email processing"""
    
    @staticmethod
    def extract_contact_info(text: str) -> Dict[str, str]:
        """
        Extract contact information from email text
        
        Args:
            text (str): Email text content
            
        Returns:
            Dict containing extracted contact information
        """
        contact_info = {
            "phone_numbers": [],
            "emails": [],
            "names": [],
            "companies": []
        }
        
        try:
            # Extract phone numbers
            phone_patterns = [
                r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
                r'\+?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,4}',
                r'\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}'
            ]
            
            for pattern in phone_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if isinstance(match, tuple):
                        phone = ''.join(match)
                    else:
                        phone = match
                    if phone not in contact_info["phone_numbers"]:
                        contact_info["phone_numbers"].append(phone)
            
            # Extract email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            contact_info["emails"] = list(set(emails))
            
            # Extract names (basic pattern)
            name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
            names = re.findall(name_pattern, text)
            contact_info["names"] = list(set(names))
            
            # Extract company names (basic pattern)
            company_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company|Co|Corporation)\b'
            companies = re.findall(company_pattern, text)
            contact_info["companies"] = list(set(companies))
            
        except Exception as e:
            logger.error(f"Error extracting contact info: {e}")
        
        return contact_info
    
    @staticmethod
    def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
        """
        Extract key phrases from email text
        
        Args:
            text (str): Email text content
            max_phrases (int): Maximum number of phrases to extract
            
        Returns:
            List of key phrases
        """
        try:
            # Remove common stop words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
            }
            
            # Split into sentences and words
            sentences = re.split(r'[.!?]+', text)
            phrases = []
            
            for sentence in sentences:
                words = re.findall(r'\b\w+\b', sentence.lower())
                # Filter out stop words and short words
                filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
                
                # Create phrases from consecutive words
                for i in range(len(filtered_words) - 1):
                    phrase = f"{filtered_words[i]} {filtered_words[i+1]}"
                    if phrase not in phrases:
                        phrases.append(phrase)
                
                # Add single important words
                for word in filtered_words:
                    if len(word) > 4 and word not in [p.split()[0] for p in phrases]:
                        phrases.append(word)
            
            # Return top phrases
            return phrases[:max_phrases]
            
        except Exception as e:
            logger.error(f"Error extracting key phrases: {e}")
            return []
    
    @staticmethod
    def extract_requirements(text: str) -> Dict[str, List[str]]:
        """
        Extract customer requirements from email text
        
        Args:
            text (str): Email text content
            
        Returns:
            Dict containing categorized requirements
        """
        requirements = {
            "technical": [],
            "support": [],
            "billing": [],
            "general": []
        }
        
        try:
            text_lower = text.lower()
            
            # Technical requirements
            tech_keywords = ["bug", "error", "crash", "broken", "not working", "issue", "problem"]
            for keyword in tech_keywords:
                if keyword in text_lower:
                    # Extract sentence containing keyword
                    sentences = re.split(r'[.!?]+', text)
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            requirements["technical"].append(sentence.strip())
                            break
            
            # Support requirements
            support_keywords = ["help", "support", "assistance", "guidance", "tutorial", "how to"]
            for keyword in support_keywords:
                if keyword in text_lower:
                    sentences = re.split(r'[.!?]+', text)
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            requirements["support"].append(sentence.strip())
                            break
            
            # Billing requirements
            billing_keywords = ["payment", "billing", "invoice", "charge", "refund", "cost", "price"]
            for keyword in billing_keywords:
                if keyword in text_lower:
                    sentences = re.split(r'[.!?]+', text)
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            requirements["billing"].append(sentence.strip())
                            break
            
            # General requirements
            general_keywords = ["request", "need", "want", "require", "looking for", "seeking"]
            for keyword in general_keywords:
                if keyword in text_lower:
                    sentences = re.split(r'[.!?]+', text)
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            requirements["general"].append(sentence.strip())
                            break
            
            # Remove duplicates
            for category in requirements:
                requirements[category] = list(set(requirements[category]))
            
        except Exception as e:
            logger.error(f"Error extracting requirements: {e}")
        
        return requirements
    
    @staticmethod
    def clean_email_text(text: str) -> str:
        """
        Clean and normalize email text
        
        Args:
            text (str): Raw email text
            
        Returns:
            Cleaned text
        """
        try:
            # Remove email headers and signatures
            lines = text.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Skip common email header patterns
                if re.match(r'^From:|^To:|^Subject:|^Date:|^Sent:|^Received:', line):
                    continue
                
                # Skip signature patterns
                if re.match(r'^--\s*$', line) or re.match(r'^Best regards|^Sincerely|^Thanks|^Regards', line):
                    break
                
                cleaned_lines.append(line)
            
            # Join lines and clean up whitespace
            cleaned_text = ' '.join(cleaned_lines)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error cleaning email text: {e}")
            return text
    
    @staticmethod
    def parse_email_message(raw_email: str) -> Dict[str, str]:
        """
        Parse raw email message into structured format
        
        Args:
            raw_email (str): Raw email message
            
        Returns:
            Dict containing parsed email components
        """
        try:
            # Parse email using email library
            msg = email.message_from_string(raw_email)
            
            parsed = {
                "subject": msg.get("subject", ""),
                "from": msg.get("from", ""),
                "to": msg.get("to", ""),
                "date": msg.get("date", ""),
                "body": ""
            }
            
            # Extract body content
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        parsed["body"] = part.get_payload(decode=True).decode()
                        break
            else:
                parsed["body"] = msg.get_payload(decode=True).decode()
            
            # Clean body text
            parsed["body"] = EmailUtils.clean_email_text(parsed["body"])
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error parsing email message: {e}")
            return {
                "subject": "",
                "from": "",
                "to": "",
                "date": "",
                "body": raw_email
            }
    
    @staticmethod
    def validate_email_address(email: str) -> bool:
        """
        Validate email address format
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))
        except Exception as e:
            logger.error(f"Error validating email: {e}")
            return False
    
    @staticmethod
    def extract_urgency_indicators(text: str) -> List[str]:
        """
        Extract urgency indicators from text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            List of urgency indicators found
        """
        urgency_indicators = []
        
        try:
            text_lower = text.lower()
    
            # Time-based urgency
            time_patterns = [
                r'today', r'tonight', r'asap', r'immediately', r'urgently',
                r'within \d+ hours?', r'right now', r'this instant'
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, text_lower)
                urgency_indicators.extend(matches)
            
            # Action-based urgency
            action_words = [
                'urgent', 'critical', 'emergency', 'desperate', 'urgently needed',
                'cannot wait', 'time sensitive', 'deadline', 'due date'
            ]
            
            for word in action_words:
                if word in text_lower:
                    urgency_indicators.append(word)
            
            # Remove duplicates
            return list(set(urgency_indicators))
            
        except Exception as e:
            logger.error(f"Error extracting urgency indicators: {e}")
            return []