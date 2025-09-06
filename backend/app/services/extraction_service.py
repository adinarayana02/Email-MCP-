import re
from typing import Dict

class ExtractionService:
    """Lightweight information extraction for support emails.

    Provides simple heuristics to extract request type, urgency, sentiment,
    and key contact details without external dependencies. This is sufficient
    for dataset-mode testing and acts as a fallback in live mode.
    """

    def extract_structured_data(self, subject: str, body: str) -> Dict:
        text = f"{subject or ''} \n {body or ''}".strip()

        request_type = self._infer_request_type(text)
        urgency_level = self._infer_urgency(text)
        sentiment = self._infer_sentiment(text)
        contacts = self._extract_contacts(text)

        return {
            "request_type": request_type,
            "urgency_level": urgency_level,
            "sentiment": sentiment,
            "contacts": contacts,
        }

    def _infer_request_type(self, text: str) -> str:
        lowered = text.lower()
        if any(k in lowered for k in ["billing", "invoice", "payment"]):
            return "billing"
        if any(k in lowered for k in ["password", "login", "reset", "access"]):
            return "account_management"
        if any(k in lowered for k in ["feature", "request", "enhancement"]):
            return "feature_request"
        if any(k in lowered for k in ["complain", "bad", "refund"]):
            return "complaint"
        if any(k in lowered for k in ["error", "issue", "bug", "not working", "crash"]):
            return "technical_support"
        return "general_inquiry"

    def _infer_urgency(self, text: str) -> str:
        lowered = text.lower()
        urgent_terms = [
            "urgent", "immediate", "asap", "critical", "cannot access", "down", "blocked"
        ]
        return "urgent" if any(k in lowered for k in urgent_terms) else "normal"

    def _infer_sentiment(self, text: str) -> str:
        lowered = text.lower()
        positive = ["thanks", "thank you", "great", "appreciate", "good"]
        negative = ["angry", "frustrated", "terrible", "bad", "unacceptable", "disappointed", "hate"]
        if any(k in lowered for k in negative):
            return "negative"
        if any(k in lowered for k in positive):
            return "positive"
        return "neutral"

    def _extract_contacts(self, text: str) -> Dict:
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
        phones = re.findall(r"(?:\+\d{1,3}[\s-]?)?(?:\(\d{3}\)|\d{3})[\s-]?\d{3}[\s-]?\d{4}", text)
        return {
            "emails": list(dict.fromkeys(emails))[:5],
            "phones": list(dict.fromkeys(phones))[:5],
        }


