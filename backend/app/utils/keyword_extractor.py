from rake_nltk import Rake
import logging
from typing import List, Set
import re
from openai import OpenAI

logger = logging.getLogger(__name__)


class KeywordExtractor:
    def __init__(self, openai_api_key: str = None):
        self.rake = Rake()
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
    
    def extract_keywords_rake(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        Extract keywords using RAKE algorithm
        """
        try:
            if not text:
                return []
            
            self.rake.extract_keywords_from_text(text)
            keywords = self.rake.get_ranked_phrases()[:max_keywords]
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords with RAKE: {str(e)}")
            return []
    
    def extract_keywords_simple(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        Simple keyword extraction by cleaning text
        """
        try:
            if not text:
                return []
            
            # Remove special characters
            text = re.sub(r'[^\w\s]', ' ', text)
            
            # Split into words
            words = text.lower().split()
            
            # Remove common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                         'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                         'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                         'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
            
            keywords = [w for w in words if w not in stop_words and len(w) > 2]
            
            # Get unique keywords maintaining order
            seen: Set[str] = set()
            unique_keywords = []
            for kw in keywords:
                if kw not in seen:
                    seen.add(kw)
                    unique_keywords.append(kw)
            
            return unique_keywords[:max_keywords]
            
        except Exception as e:
            logger.error(f"Error in simple keyword extraction: {str(e)}")
            return []
    
    def extract_keywords_with_ai(self, text: str, max_keywords: int = 5) -> List[str]:
        """
        Extract keywords using OpenAI (more accurate but costs API calls)
        """
        try:
            if not self.openai_client or not text:
                return self.extract_keywords_rake(text, max_keywords)
            
            prompt = f"""Extract the {max_keywords} most important keywords or key phrases from the following text.
Return only the keywords, separated by commas, without any additional text.

Text: {text[:500]}

Keywords:"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a keyword extraction assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            keywords_text = response.choices[0].message.content.strip()
            keywords = [k.strip() for k in keywords_text.split(',')]
            
            return keywords[:max_keywords]
            
        except Exception as e:
            logger.error(f"Error extracting keywords with AI: {str(e)}")
            return self.extract_keywords_rake(text, max_keywords)
    
    def extract_keywords(self, text: str, max_keywords: int = 5, use_ai: bool = False) -> List[str]:
        """
        Main keyword extraction method
        """
        if use_ai and self.openai_client:
            return self.extract_keywords_with_ai(text, max_keywords)
        else:
            # Try RAKE first, fall back to simple
            keywords = self.extract_keywords_rake(text, max_keywords)
            if not keywords:
                keywords = self.extract_keywords_simple(text, max_keywords)
            return keywords