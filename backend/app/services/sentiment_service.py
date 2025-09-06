from transformers import pipeline
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class SentimentService:
    """Service for analyzing email sentiment"""
    
    def __init__(self):
        try:
            # Use a known stable model to avoid heavy deps and torch restrictions
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
                return_all_scores=True
            )
            logger.info("Sentiment analysis pipeline initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sentiment pipeline: {e}")
            self.sentiment_pipeline = None
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of given text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict containing sentiment analysis results
        """
        if not self.sentiment_pipeline:
            return self._fallback_sentiment_analysis(text)
        
        try:
            # Clean and prepare text
            cleaned_text = self._preprocess_text(text)
            
            # Analyze sentiment
            results = self.sentiment_pipeline(cleaned_text)
            
            # Extract scores
            sentiment_scores = {}
            for result in results[0]:
                sentiment_scores[result['label']] = result['score']
            
            # Determine primary sentiment
            primary_sentiment = max(sentiment_scores.items(), key=lambda x: x[1])
            
            # Map to our sentiment categories
            mapped_sentiment = self._map_sentiment(primary_sentiment[0])
            
            return {
                "sentiment": mapped_sentiment,
                "confidence": primary_sentiment[1],
                "scores": sentiment_scores,
                "raw_results": results
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return self._fallback_sentiment_analysis(text)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Remove extra whitespace and limit length
        cleaned = " ".join(text.split())
        # Limit to reasonable length for the model
        if len(cleaned) > 500:
            cleaned = cleaned[:500]
        return cleaned
    
    def _map_sentiment(self, label: str) -> str:
        """Map model labels to our sentiment categories"""
        label_lower = label.lower()
        
        if "positive" in label_lower or "pos" in label_lower:
            return "positive"
        elif "negative" in label_lower or "neg" in label_lower:
            return "negative"
        else:
            return "neutral"
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using keyword-based approach"""
        text_lower = text.lower()
        
        # Define positive and negative keywords
        positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "happy", "pleased", "satisfied", "thank", "appreciate", "love",
            "awesome", "brilliant", "outstanding", "perfect", "superb"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "horrible", "disappointed", "angry",
            "frustrated", "upset", "annoyed", "hate", "dislike", "problem",
            "issue", "broken", "failed", "error", "crash", "slow"
        ]
        
        # Count occurrences
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Determine sentiment
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.8, 0.5 + (positive_count * 0.1))
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.8, 0.5 + (negative_count * 0.1))
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "method": "keyword_fallback",
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    
    def batch_analyze_sentiment(self, texts: list) -> list:
        """Analyze sentiment for multiple texts"""
        results = []
        for text in texts:
            result = self.analyze_sentiment(text)
            results.append(result)
        return results
