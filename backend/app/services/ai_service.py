import openai
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import json
import logging
from typing import Dict, Tuple, List
import re
from datetime import datetime

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        
        # Initialize sentiment analysis pipeline
        try:
            # Prefer a stable light model to avoid torch >=2.6 requirement
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
                return_all_scores=True
            )
        except Exception as e:
            logger.warning(f"Could not initialize sentiment model: {e}")
            self.sentiment_analyzer = None
        
        # Load knowledge base
        self.knowledge_base = self._load_knowledge_base()

        # Fallback sentiment keyword lists
        self._positive_keywords = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "happy", "pleased", "satisfied", "thank", "appreciate", "love",
            "awesome", "brilliant", "outstanding", "perfect", "superb"
        ]
        self._negative_keywords = [
            "bad", "terrible", "awful", "horrible", "disappointed", "angry",
            "frustrated", "upset", "annoyed", "hate", "dislike", "problem",
            "issue", "broken", "failed", "error", "crash", "slow"
        ]

    def _load_knowledge_base(self) -> Dict:
        """Load knowledge base for RAG"""
        try:
            # Resolve path relative to project root (backend/data/knowledge_base.json)
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            kb_path = os.path.join(base_dir, 'data', 'knowledge_base.json')
            with open(kb_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create comprehensive knowledge base
            default_kb = {
                "general": {
                    "greeting": "Thank you for contacting our support team. We're here to help you with any questions or concerns you may have.",
                    "closing": "If you have any further questions, please don't hesitate to reach out. We're committed to providing you with the best possible support.",
                    "escalation": "I understand this is important to you. Let me escalate this to our senior support team for immediate attention."
                },
                "technical_issues": {
                    "login_problems": "For login issues, please try the following steps: 1) Clear your browser cache and cookies, 2) Reset your password, 3) Check if Caps Lock is enabled, 4) Try a different browser. If the issue persists, our technical team will investigate further.",
                    "connectivity": "Please check your internet connection and try again. If you're still experiencing issues, try: 1) Restarting your router, 2) Using a different network, 3) Checking firewall settings.",
                    "performance": "We're aware of some performance issues and our engineering team is actively working on optimization. In the meantime, try refreshing the page or clearing your browser cache.",
                    "mobile_app": "For mobile app issues, please try: 1) Updating to the latest version, 2) Restarting the app, 3) Checking device storage space, 4) Reinstalling the app if necessary."
                },
                "billing": {
                    "payment_failed": "For payment issues, please verify: 1) Your payment method details are correct, 2) You have sufficient funds, 3) Your card hasn't expired. If the problem continues, please contact your bank or try an alternative payment method.",
                    "refund_request": "Refund requests are typically processed within 5-7 business days. Please provide your order number and reason for the refund. Our billing team will review your request and process it accordingly.",
                    "billing_inquiry": "For billing inquiries, please provide your account details and specific question. Our billing specialist will review your account and provide a detailed explanation.",
                    "subscription": "To manage your subscription, please visit your account settings or contact our billing team. We can help with upgrades, downgrades, or cancellations."
                },
                "product_info": {
                    "features": "Our platform offers comprehensive features including: real-time collaboration, advanced analytics, secure data storage, mobile access, and 24/7 support. Would you like me to provide more details about any specific feature?",
                    "pricing": "For detailed pricing information, please visit our pricing page or contact our sales team. We offer flexible plans to meet different business needs and can provide custom quotes for enterprise customers.",
                    "updates": "We regularly release updates to improve functionality and security. You can check for updates in your account settings or enable automatic updates for the best experience."
                },
                "account_management": {
                    "password_reset": "To reset your password, please use the 'Forgot Password' link on the login page. You'll receive an email with reset instructions. If you don't receive the email, check your spam folder.",
                    "profile_update": "You can update your profile information in your account settings. Changes are typically reflected immediately, but some updates may require verification.",
                    "two_factor": "Two-factor authentication adds an extra layer of security to your account. You can enable it in your security settings and choose between SMS, email, or authenticator app verification."
                }
            }
            
            # Save default knowledge base
            with open(kb_path, 'w') as f:
                json.dump(default_kb, f, indent=2)
            
            return default_kb

    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment of email text"""
        try:
            # Use transformers pipeline
            results = self.sentiment_analyzer(text)
            
            if isinstance(results[0], list):
                # Handle multiple scores format
                sentiment_scores = {item['label'].lower(): item['score'] for item in results[0]}
                
                # Map labels to our format
                label_mapping = {
                    'positive': 'positive',
                    'negative': 'negative', 
                    'neutral': 'neutral',
                    'label_0': 'negative',  # Some models use numeric labels
                    'label_1': 'neutral',
                    'label_2': 'positive'
                }
                
                mapped_scores = {}
                for label, score in sentiment_scores.items():
                    mapped_label = label_mapping.get(label, label)
                    if mapped_label in ['positive', 'negative', 'neutral']:
                        mapped_scores[mapped_label] = score
                
                if mapped_scores:
                    sentiment = max(mapped_scores, key=mapped_scores.get)
                    confidence = mapped_scores[sentiment]
                else:
                    sentiment, confidence = 'neutral', 0.5
            else:
                # Handle single result format
                result = results[0]
                sentiment = result['label'].lower()
                confidence = result['score']
                
                # Map common labels
                if sentiment in ['label_0', 'negative']:
                    sentiment = 'negative'
                elif sentiment in ['label_1', 'neutral']:
                    sentiment = 'neutral'
                elif sentiment in ['label_2', 'positive']:
                    sentiment = 'positive'
            
            return sentiment, confidence
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            # Fallback to keyword-based analysis
            return self._keyword_based_sentiment(text)

    def _keyword_based_sentiment(self, text: str) -> Tuple[str, float]:
        """Fallback keyword-based sentiment analysis"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self._positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self._negative_keywords if word in text_lower)
        
        if negative_count > positive_count:
            return 'negative', min(0.8, 0.5 + (negative_count * 0.1))
        elif positive_count > negative_count:
            return 'positive', min(0.8, 0.5 + (positive_count * 0.1))
        else:
            return 'neutral', 0.5

    def determine_priority(self, subject: str, body: str) -> Tuple[str, float]:
        """Determine email priority based on content with enhanced logic"""
        text = (subject + " " + body).lower()
        
        # Enhanced priority keywords
        urgent_keywords = [
            'urgent', 'critical', 'emergency', 'immediately', 'asap', 'right now',
            'cannot access', 'system down', 'broken', 'not working', 'error',
            'urgent help', 'critical issue', 'emergency support', 'urgent request'
        ]
        
        high_keywords = [
            'important', 'priority', 'high priority', 'need help', 'support needed',
            'issue', 'problem', 'trouble', 'difficulty', 'challenge', 'concern'
        ]
        
        low_keywords = [
            'general inquiry', 'information request', 'question', 'curious',
            'just wondering', 'out of curiosity', 'when you have time'
        ]
        
        urgent_score = sum(2 for keyword in urgent_keywords if keyword in text)
        high_score = sum(1 for keyword in high_keywords if keyword in text)
        low_score = sum(1 for keyword in low_keywords if keyword in text)
        
        # Check for time-sensitive indicators
        time_indicators = ['today', 'tonight', 'this week', 'deadline', 'due date']
        time_urgency = sum(1 for indicator in time_indicators if indicator in text)
        
        # Calculate final priority score
        total_score = urgent_score + high_score - low_score + time_urgency
        
        if urgent_score >= 2 or total_score >= 4:
            return 'urgent', min(0.95, 0.8 + (urgent_score * 0.05))
        elif high_score >= 2 or total_score >= 2:
            return 'high', min(0.85, 0.6 + (high_score * 0.1))
        elif low_score >= 2:
            return 'low', max(0.2, 0.3 - (low_score * 0.05))
        else:
            return 'normal', 0.5

    def categorize_email(self, subject: str, body: str) -> str:
        """Enhanced email categorization with more specific categories"""
        text = (subject + " " + body).lower()
        
        categories = {
            'technical_support': ['login', 'password', 'access', 'error', 'bug', 'not working', 'technical', 'system', 'app', 'mobile', 'website', 'platform'],
            'billing': ['payment', 'charge', 'bill', 'invoice', 'refund', 'subscription', 'pricing', 'cost', 'money', 'credit card', 'debit card'],
            'general_inquiry': ['information', 'question', 'inquiry', 'details', 'how to', 'what is', 'can you tell me', 'i want to know'],
            'complaint': ['complaint', 'dissatisfied', 'angry', 'frustrated', 'terrible', 'awful', 'bad experience', 'unhappy', 'disappointed'],
            'feature_request': ['feature', 'suggestion', 'improvement', 'enhance', 'add', 'new functionality', 'capability', 'option'],
            'account_management': ['account', 'profile', 'settings', 'update', 'change', 'modify', 'personal information', 'preferences'],
            'product_support': ['product', 'service', 'how to use', 'tutorial', 'guide', 'instructions', 'help with'],
            'sales': ['purchase', 'buy', 'order', 'sales', 'pricing', 'quote', 'demo', 'trial', 'subscription plan']
        }
        
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(2 for keyword in keywords if keyword in text)  # Weighted scoring
            category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return 'general_inquiry'

    def extract_information(self, subject: str, body: str, sender: str) -> Dict:
        """Enhanced information extraction from email"""
        info = {
            'sender_email': sender,
            'contact_phone': None,
            'customer_name': None,
            'product_mentioned': None,
            'account_id': None,
            'order_id': None,
            'urgency_indicators': [],
            'technical_details': [],
            'business_impact': None,
            'preferred_contact': None
        }
        
        text = subject + " " + body
        
        # Extract phone numbers
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            info['contact_phone'] = phones[0]
        
        # Extract names (enhanced patterns)
        name_patterns = [
            r'my name is ([A-Za-z\s]+)',
            r'i am ([A-Za-z\s]+)',
            r'this is ([A-Za-z\s]+)',
            r'from ([A-Za-z\s]+)',
            r'regards,?\s*([A-Za-z\s]+)',
            r'sincerely,?\s*([A-Za-z\s]+)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['customer_name'] = match.group(1).strip()
                break
        
        # Extract IDs and references
        account_match = re.search(r'account[#\s]*:?\s*([A-Za-z0-9\-_]+)', text, re.IGNORECASE)
        if account_match:
            info['account_id'] = account_match.group(1)
        
        order_match = re.search(r'order[#\s]*:?\s*([A-Za-z0-9\-_]+)', text, re.IGNORECASE)
        if order_match:
            info['order_id'] = order_match.group(1)
        
        # Extract product mentions
        product_keywords = ['product', 'service', 'platform', 'app', 'software', 'tool']
        for keyword in product_keywords:
            if keyword in text.lower():
                # Look for product name after keyword
                pattern = rf"{keyword}[:\s]+([A-Za-z0-9\s\-_]+)"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    info['product_mentioned'] = match.group(1).strip()
                    break
        
        # Find urgency indicators
        urgent_keywords = ['urgent', 'critical', 'emergency', 'immediately', 'asap', 'right now']
        for keyword in urgent_keywords:
            if keyword in text.lower():
                info['urgency_indicators'].append(keyword)
        
        # Extract technical details
        tech_keywords = ['error', 'bug', 'crash', 'freeze', 'slow', 'performance', 'loading']
        for keyword in tech_keywords:
            if keyword in text.lower():
                info['technical_details'].append(keyword)
        
        # Determine business impact
        impact_keywords = {
            'high': ['cannot work', 'blocked', 'stopped', 'broken', 'system down'],
            'medium': ['difficult', 'challenging', 'problem', 'issue'],
            'low': ['question', 'inquiry', 'information', 'curious']
        }
        
        for impact_level, keywords in impact_keywords.items():
            if any(keyword in text.lower() for keyword in keywords):
                info['business_impact'] = impact_level
                break
        
        # Determine preferred contact method
        if info['contact_phone']:
            info['preferred_contact'] = 'phone'
        elif 'call me' in text.lower() or 'phone' in text.lower():
            info['preferred_contact'] = 'phone'
        elif 'email me' in text.lower() or 'reply to' in text.lower():
            info['preferred_contact'] = 'email'
        
        return info

    def generate_response(self, email_subject: str, email_body: str, sender: str, 
                         sentiment: str, priority: str, category: str, 
                         extracted_info: Dict) -> Tuple[str, float]:
        """Generate AI response using OpenAI GPT with enhanced RAG"""
        try:
            # Prepare context from knowledge base
            kb_context = self._get_relevant_kb_context(category, email_body, priority)
            
            # Create enhanced prompt
            prompt = self._create_enhanced_response_prompt(
                email_subject, email_body, sender, sentiment, 
                priority, category, extracted_info, kb_context
            )
            
            # Generate response using OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional, empathetic customer support representative with expertise in technical support, billing, and general inquiries. Always maintain a helpful and understanding tone."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            generated_text = response.choices[0].message.content.strip()
            confidence = 0.9  # High confidence for GPT responses
            
            return generated_text, confidence
            
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {e}")
            return self._generate_fallback_response(category, sentiment, priority, extracted_info)
            
    def generate_context_aware_response(self, subject, body, sender, sentiment, priority, category, extracted_info, context_data=None, response_tone="professional", include_knowledge_base=True) -> Tuple[str, float]:
        """Generate a context-aware response to an email using LLM"""
        try:
            # Prepare prompt with context
            prompt = self._prepare_response_prompt(
                subject, body, sender, sentiment, priority, category,
                extracted_info, context_data, response_tone, include_knowledge_base
            )
            
            # Call OpenAI API with updated API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful customer support assistant that writes professional, concise, and helpful email responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.5
            )
            
            response_text = response.choices[0].message.content.strip()
            confidence = 0.85  # Placeholder for confidence score
            
            return response_text, confidence
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            # Fallback to template response
            return self._generate_fallback_response(category, priority), 0.5

    def _get_relevant_kb_context(self, category: str, email_body: str, priority: str) -> str:
        """Get relevant context from knowledge base with priority consideration"""
        context_parts = []
        
        # Add general context
        if 'general' in self.knowledge_base:
            if priority == 'urgent':
                context_parts.append(self.knowledge_base['general']['escalation'])
            else:
                context_parts.append(self.knowledge_base['general']['greeting'])
        
        # Add category-specific context
        email_lower = email_body.lower()
        
        if category == 'technical_support' and 'technical_issues' in self.knowledge_base:
            if any(word in email_lower for word in ['login', 'password', 'access']):
                context_parts.append(self.knowledge_base['technical_issues']['login_problems'])
            elif any(word in email_lower for word in ['slow', 'performance', 'loading']):
                context_parts.append(self.knowledge_base['technical_issues']['performance'])
            elif any(word in email_lower for word in ['connection', 'network', 'connectivity']):
                context_parts.append(self.knowledge_base['technical_issues']['connectivity'])
            elif any(word in email_lower for word in ['mobile', 'app', 'phone']):
                context_parts.append(self.knowledge_base['technical_issues']['mobile_app'])
        
        elif category == 'billing' and 'billing' in self.knowledge_base:
            if any(word in email_lower for word in ['payment', 'charge', 'failed']):
                context_parts.append(self.knowledge_base['billing']['payment_failed'])
            elif any(word in email_lower for word in ['refund', 'return', 'money back']):
                context_parts.append(self.knowledge_base['billing']['refund_request'])
            elif any(word in email_lower for word in ['subscription', 'plan', 'billing cycle']):
                context_parts.append(self.knowledge_base['billing']['subscription'])
            else:
                context_parts.append(self.knowledge_base['billing']['billing_inquiry'])
        
        elif category in ['general_inquiry', 'feature_request'] and 'product_info' in self.knowledge_base:
            if any(word in email_lower for word in ['price', 'cost', 'pricing']):
                context_parts.append(self.knowledge_base['product_info']['pricing'])
            elif any(word in email_lower for word in ['update', 'new version', 'latest']):
                context_parts.append(self.knowledge_base['product_info']['updates'])
            else:
                context_parts.append(self.knowledge_base['product_info']['features'])
        
        elif category == 'account_management' and 'account_management' in self.knowledge_base:
            if any(word in email_lower for word in ['password', 'reset', 'forgot']):
                context_parts.append(self.knowledge_base['account_management']['password_reset'])
            elif any(word in email_lower for word in ['profile', 'update', 'change']):
                context_parts.append(self.knowledge_base['account_management']['profile_update'])
            elif any(word in email_lower for word in ['two factor', '2fa', 'security']):
                context_parts.append(self.knowledge_base['account_management']['two_factor'])
        
        return " ".join(context_parts)

    def _create_enhanced_response_prompt(self, subject: str, body: str, sender: str, 
                                       sentiment: str, priority: str, category: str, 
                                       extracted_info: Dict, kb_context: str) -> str:
        """Create enhanced prompt for response generation"""
        
        # Extract customer name if available
        customer_name = extracted_info.get('customer_name', 'Valued Customer')
        
        # Determine tone based on sentiment and priority
        if priority == 'urgent':
            tone_instruction = "Be very responsive and show immediate attention to their urgent matter"
        elif sentiment == 'negative':
            tone_instruction = "Be especially empathetic and understanding, acknowledge their frustration"
        else:
            tone_instruction = "Be professional, friendly, and helpful"
        
        prompt = f"""
You are a professional customer support representative. Generate a helpful, empathetic response to the following customer email.

CUSTOMER EMAIL:
From: {sender}
Subject: {subject}
Body: {body}

ANALYSIS:
- Sentiment: {sentiment}
- Priority: {priority}
- Category: {category}
- Customer Info: {json.dumps(extracted_info, indent=2)}

KNOWLEDGE BASE CONTEXT:
{kb_context}

RESPONSE GUIDELINES:
1. {tone_instruction}
2. Address the customer by name if available: {customer_name}
3. {"Acknowledge their frustration empathetically and assure immediate attention" if sentiment == "negative" else "Thank them for contacting us"}
4. {"Mark this as high priority and provide immediate next steps" if priority == "urgent" else "Provide helpful guidance and next steps"}
5. Include relevant information from the knowledge base
6. Offer specific solutions or next steps where appropriate
7. Set clear expectations for follow-up or resolution time
8. End with a professional closing and offer additional support

Generate a response that is 200-300 words and addresses their specific needs:
"""
        return prompt

    def _generate_fallback_response(self, category: str, sentiment: str, priority: str, extracted_info: Dict) -> Tuple[str, float]:
        """Generate enhanced fallback response when OpenAI is not available"""
        
        customer_name = extracted_info.get('customer_name', 'Valued Customer')
        
        # Enhanced response templates with priority consideration
        responses = {
            'technical_support': f"""Dear {customer_name},

Thank you for contacting our technical support team. We understand you're experiencing technical difficulties, and we're committed to resolving this issue promptly.

{"This has been marked as a high priority case, and our technical team will address it immediately." if priority in ['urgent', 'high'] else "Our technical team will review your case and provide you with detailed steps to resolve the problem."}

{"For immediate assistance, please try clearing your browser cache or restarting the application." if priority == 'urgent' else "In the meantime, please try the basic troubleshooting steps we've outlined in our help documentation."}

We appreciate your patience and will follow up with you {"within 2 hours" if priority == 'urgent' else "within 24 hours"} with a resolution.

Best regards,
Technical Support Team""",

            'billing': f"""Dear {customer_name},

Thank you for reaching out regarding your billing inquiry. We take all billing matters seriously and want to ensure everything is resolved to your satisfaction.

{"This has been marked as a priority case, and our billing specialist will review it immediately." if priority in ['urgent', 'high'] else "Our billing specialist will review your account details and provide clarification on any charges or concerns you may have."}

Please allow {"1 business day" if priority in ['urgent', 'high'] else "1-2 business days"} for a complete review and response.

If you have any urgent billing concerns, please don't hesitate to contact us directly.

Best regards,
Billing Support Team""",

            'complaint': f"""Dear {customer_name},

Thank you for bringing your concerns to our attention. We sincerely apologize for any inconvenience you may have experienced, and we take your feedback very seriously.

{"This has been escalated to our senior support team for immediate attention." if priority in ['urgent', 'high'] else "We are committed to resolving this matter promptly and ensuring your experience with our service meets the high standards you expect."}

A {"senior team member will personally review your case and contact you within 2 hours" if priority in ['urgent', 'high'] else "senior team member will personally review your case and contact you within 24 hours"}.

We value your business and appreciate the opportunity to make this right.

Best regards,
Customer Relations Team""",

            'general_inquiry': f"""Dear {customer_name},

Thank you for your inquiry. We're happy to help provide you with the information you need.

{"This has been marked as a priority inquiry, and our team will address it promptly." if priority in ['urgent', 'high'] else "Based on your question, our team will gather the relevant details and provide you with a comprehensive response."}

We strive to answer all inquiries within {"4 hours" if priority in ['urgent', 'high'] else "1-2 business days"}.

If you have any additional questions in the meantime, please feel free to reach out to us.

Best regards,
Customer Support Team"""
        }
        
        # Get base response and adjust based on priority and sentiment
        base_response = responses.get(category, responses['general_inquiry'])
        
        if sentiment == 'negative':
            base_response = base_response.replace('Thank you for', 'We sincerely apologize and thank you for')
            base_response = base_response.replace('We appreciate', 'We deeply appreciate')
        
        if priority == 'urgent':
            base_response = base_response.replace('Best regards,', 'We\'re on it!\n\nBest regards,')
        
        return base_response, 0.75  # Good confidence for enhanced fallback responses