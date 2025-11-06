import httpx
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GoogleTrendsService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search.json"
    
    def get_trending_searches(self, geo: str = "US", date: str = "now 7-d") -> Dict[str, Any]:
        """
        Fetch trending searches from Google Trends
        
        Args:
            geo: Geographic location code (e.g., 'US', 'GB', 'IN')
            date: Time period (e.g., 'now 7-d', 'today 1-m', 'today 12-m')
            
        Returns:
            Dictionary containing trending searches data
        """
        try:
            logger.info(f"Fetching Google Trends for geo: {geo}, date: {date}")
            
            # Get trending queries (related queries can show what's trending)
            params = {
                "engine": "google_trends",
                "data_type": "RELATED_QUERIES",
                "q": "",  # Empty query to get overall trends
                "geo": geo,
                "date": date,
                "api_key": self.api_key
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching Google Trends: {str(e)}")
            return {}
    
    def get_interest_over_time(self, queries: List[str], geo: str = "US", date: str = "now 7-d") -> Dict[str, Any]:
        """
        Get interest over time for specific queries
        
        Args:
            queries: List of search queries (max 5)
            geo: Geographic location code
            date: Time period
            
        Returns:
            Interest over time data
        """
        try:
            # Join queries with comma
            q = ",".join(queries[:5])  # Max 5 queries
            
            params = {
                "engine": "google_trends",
                "data_type": "TIMESERIES",
                "q": q,
                "geo": geo,
                "date": date,
                "api_key": self.api_key
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching interest over time: {str(e)}")
            return {}
    
    def get_trending_now(self, geo: str = "US") -> List[Dict[str, Any]]:
        """
        Get what's trending now on Google
        Uses multiple broad queries to find trending topics
        """
        all_trends = []

        # Use broad popular queries to get trending related topics and queries
        base_queries = ["trending", "viral", "news", "popular"]

        try:
            for base_query in base_queries:
                try:
                    # Get RELATED_TOPICS
                    topics_params = {
                        "engine": "google_trends",
                        "data_type": "RELATED_TOPICS",
                        "q": base_query,
                        "geo": geo,
                        "api_key": self.api_key
                    }

                    with httpx.Client(timeout=30.0) as client:
                        response = client.get(self.base_url, params=topics_params)
                        response.raise_for_status()
                        topics_data = response.json()

                    # Extract rising topics
                    if "related_topics" in topics_data:
                        if "rising" in topics_data["related_topics"]:
                            for item in topics_data["related_topics"]["rising"][:10]:
                                topic = item.get("topic", {})
                                all_trends.append({
                                    "query": topic.get("title", ""),
                                    "value": item.get("extracted_value", 100),
                                    "type": "rising",
                                    "link": topic.get("link", "")
                                })

                        # Extract top topics
                        if "top" in topics_data["related_topics"]:
                            for item in topics_data["related_topics"]["top"][:5]:
                                topic = item.get("topic", {})
                                all_trends.append({
                                    "query": topic.get("title", ""),
                                    "value": item.get("extracted_value", 50),
                                    "type": "top",
                                    "link": topic.get("link", "")
                                })

                    # Get RELATED_QUERIES
                    queries_params = {
                        "engine": "google_trends",
                        "data_type": "RELATED_QUERIES",
                        "q": base_query,
                        "geo": geo,
                        "api_key": self.api_key
                    }

                    with httpx.Client(timeout=30.0) as client:
                        response = client.get(self.base_url, params=queries_params)
                        response.raise_for_status()
                        queries_data = response.json()

                    # Extract rising queries
                    if "related_queries" in queries_data:
                        if "rising" in queries_data["related_queries"]:
                            for item in queries_data["related_queries"]["rising"][:10]:
                                all_trends.append({
                                    "query": item.get("query", ""),
                                    "value": item.get("extracted_value", 100),
                                    "type": "rising",
                                    "link": item.get("link", "")
                                })

                        # Extract top queries
                        if "top" in queries_data["related_queries"]:
                            for item in queries_data["related_queries"]["top"][:5]:
                                all_trends.append({
                                    "query": item.get("query", ""),
                                    "value": item.get("extracted_value", 50),
                                    "type": "top",
                                    "link": item.get("link", "")
                                })

                except Exception as e:
                    logger.warning(f"Error fetching trends for query '{base_query}': {str(e)}")
                    continue

            # Remove duplicates based on query
            seen = set()
            unique_trends = []
            for trend in all_trends:
                query = trend.get("query", "").lower()
                if query and query not in seen:
                    seen.add(query)
                    unique_trends.append(trend)

            logger.info(f"Fetched {len(unique_trends)} unique Google Trends items")
            return unique_trends

        except Exception as e:
            logger.error(f"Error fetching trending now: {str(e)}", exc_info=True)
            return []
    
    def extract_topics_from_google_trends(self, trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract topics from Google Trends data
        """
        topics = []
        
        for trend in trends[:30]:  # Top 30 trends
            topics.append({
                "topic": trend.get("query", ""),
                "source": trend.get("type", "unknown"),
                "interest": trend.get("value", 0),
                "link": trend.get("link", "")
            })
        
        return topics