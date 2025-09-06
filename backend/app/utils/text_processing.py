import re
import string
from typing import List, Dict, Tuple, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class TextProcessor:
    """Utility class for text processing operations"""
    
    @staticmethod
    def remove_special_characters(text: str, keep_spaces: bool = True) -> str:
        """
        Remove special characters from text
        
        Args:
            text (str): Input text
            keep_spaces (bool): Whether to keep spaces
            
        Returns:
            str: Cleaned text
        """
        try:
            if keep_spaces:
                # Keep letters, numbers, and spaces
                pattern = r'[^a-zA-Z0-9\s]'
            else:
                # Keep only letters and numbers
                pattern = r'[^a-zA-Z0-9]'
            
            cleaned = re.sub(pattern, '', text)
            return cleaned
        except Exception as e:
            logger.error(f"Error removing special characters: {e}")
            return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace in text
        
        Args:
            text (str): Input text
            
        Returns:
            str: Text with normalized whitespace
        """
        try:
            # Replace multiple spaces with single space
            normalized = re.sub(r'\s+', ' ', text)
            # Remove leading/trailing whitespace
            return normalized.strip()
        except Exception as e:
            logger.error(f"Error normalizing whitespace: {e}")
            return text
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """
        Extract sentences from text
        
        Args:
            text (str): Input text
            
        Returns:
            List[str]: List of sentences
        """
        try:
            # Split on sentence endings
            sentences = re.split(r'[.!?]+', text)
            # Clean and filter empty sentences
            cleaned_sentences = [s.strip() for s in sentences if s.strip()]
            return cleaned_sentences
        except Exception as e:
            logger.error(f"Error extracting sentences: {e}")
            return [text]
    
    @staticmethod
    def extract_words(text: str, min_length: int = 3) -> List[str]:
        """
        Extract words from text
        
        Args:
            text (str): Input text
            min_length (int): Minimum word length
            
        Returns:
            List[str]: List of words
        """
        try:
            # Remove punctuation and split into words
            words = re.findall(r'\b\w+\b', text.lower())
            # Filter by minimum length
            filtered_words = [word for word in words if len(word) >= min_length]
            return filtered_words
        except Exception as e:
            logger.error(f"Error extracting words: {e}")
            return []
    
    @staticmethod
    def get_word_frequency(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Get word frequency in text
        
        Args:
            text (str): Input text
            top_n (int): Number of top words to return
            
        Returns:
            List[Tuple[str, int]]: List of (word, count) tuples
        """
        try:
            words = TextProcessor.extract_words(text)
            word_counts = Counter(words)
            return word_counts.most_common(top_n)
        except Exception as e:
            logger.error(f"Error getting word frequency: {e}")
            return []
    
    @staticmethod
    def remove_stop_words(text: str, custom_stop_words: Optional[List[str]] = None) -> str:
        """
        Remove stop words from text
        
        Args:
            text (str): Input text
            custom_stop_words (Optional[List[str]]): Custom stop words to add
            
        Returns:
            str: Text with stop words removed
        """
        try:
            # Common English stop words
            default_stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
                'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
                'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
            }
            
            if custom_stop_words:
                stop_words = default_stop_words.union(set(custom_stop_words))
            else:
                stop_words = default_stop_words
            
            words = text.split()
            filtered_words = [word for word in words if word.lower() not in stop_words]
            
            return ' '.join(filtered_words)
            
        except Exception as e:
            logger.error(f"Error removing stop words: {e}")
            return text
    
    @staticmethod
    def extract_n_grams(text: str, n: int = 2) -> List[str]:
        """
        Extract n-grams from text
        
        Args:
            text (str): Input text
            n (int): Size of n-grams
            
        Returns:
            List[str]: List of n-grams
        """
        try:
            words = TextProcessor.extract_words(text)
            n_grams = []
            
            for i in range(len(words) - n + 1):
                n_gram = ' '.join(words[i:i+n])
                n_grams.append(n_gram)
            
            return n_grams
            
        except Exception as e:
            logger.error(f"Error extracting n-grams: {e}")
            return []
    
    @staticmethod
    def calculate_text_statistics(text: str) -> Dict[str, any]:
        """
        Calculate various text statistics
        
        Args:
            text (str): Input text
            
        Returns:
            Dict containing text statistics
        """
        try:
            stats = {}
            
            # Basic counts
            stats['character_count'] = len(text)
            stats['word_count'] = len(text.split())
            stats['sentence_count'] = len(TextProcessor.extract_sentences(text))
            stats['paragraph_count'] = len([p for p in text.split('\n\n') if p.strip()])
            
            # Word analysis
            words = TextProcessor.extract_words(text)
            stats['unique_word_count'] = len(set(words))
            stats['average_word_length'] = sum(len(word) for word in words) / len(words) if words else 0
            
            # Readability metrics (simplified)
            if stats['sentence_count'] > 0 and stats['word_count'] > 0:
                stats['average_sentence_length'] = stats['word_count'] / stats['sentence_count']
            else:
                stats['average_sentence_length'] = 0
            
            # Most common words
            stats['top_words'] = TextProcessor.get_word_frequency(text, 5)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating text statistics: {e}")
            return {}
    
    @staticmethod
    def find_keywords_in_text(text: str, keywords: List[str]) -> Dict[str, List[str]]:
        """
        Find occurrences of keywords in text
        
        Args:
            text (str): Input text
            keywords (List[str]): List of keywords to search for
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping keywords to context sentences
        """
        try:
            results = {}
            text_lower = text.lower()
            sentences = TextProcessor.extract_sentences(text)
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in text_lower:
                    # Find sentences containing the keyword
                    containing_sentences = []
                    for sentence in sentences:
                        if keyword_lower in sentence.lower():
                            containing_sentences.append(sentence.strip())
                    
                    results[keyword] = containing_sentences
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding keywords: {e}")
            return {}
    
    @staticmethod
    def summarize_text(text: str, max_sentences: int = 3) -> str:
        """
        Create a simple summary of text
        
        Args:
            text (str): Input text
            max_sentences (int): Maximum number of sentences in summary
            
        Returns:
            str: Text summary
        """
        try:
            sentences = TextProcessor.extract_sentences(text)
            
            if len(sentences) <= max_sentences:
                return text
            
            # Simple approach: take first few sentences
            summary_sentences = sentences[:max_sentences]
            return '. '.join(summary_sentences) + '.'
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return text
    
    @staticmethod
    def clean_html_tags(text: str) -> str:
        """
        Remove HTML tags from text
        
        Args:
            text (str): Input text with HTML tags
            
        Returns:
            str: Clean text without HTML tags
        """
        try:
            # Remove HTML tags
            clean_text = re.sub(r'<[^>]+>', '', text)
            # Remove extra whitespace
            clean_text = TextProcessor.normalize_whitespace(clean_text)
            return clean_text
        except Exception as e:
            logger.error(f"Error cleaning HTML tags: {e}")
            return text
