from serpapi import GoogleSearch
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GoogleTrendsDetailsService:
    """Service for fetching detailed Google Trends data using SerpAPI"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_interest_over_time(
        self,
        query: str,
        geo: str = "US",
        date: str = "today 12-m"
    ) -> Dict[str, Any]:
        """
        Fetch interest over time data for a specific query.

        Args:
            query: Search query to analyze
            geo: Geographic location code (e.g., 'US', 'LK', 'IN')
            date: Time period (e.g., 'today 12-m', 'today 3-m', 'today 1-m')

        Returns:
            Dictionary with timeline_data containing timestamps and values
        """
        try:
            params = {
                "engine": "google_trends",
                "q": query,
                "geo": geo,
                "date": date,
                "data_type": "TIMESERIES",
                "api_key": self.api_key
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            interest_over_time = results.get("interest_over_time", {})
            logger.info(f"Fetched interest over time for '{query}' in {geo}")

            return interest_over_time

        except Exception as e:
            logger.error(f"Error fetching interest over time: {str(e)}")
            return {}

    def get_related_topics(
        self,
        query: str,
        geo: str = "US",
        date: str = "today 12-m"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch related topics for a specific query.

        Args:
            query: Search query to analyze
            geo: Geographic location code (e.g., 'US', 'LK', 'IN')
            date: Time period (e.g., 'today 12-m', 'today 3-m', 'today 1-m')

        Returns:
            Dictionary with 'rising' and 'top' lists of related topics
        """
        try:
            params = {
                "engine": "google_trends",
                "q": query,
                "geo": geo,
                "date": date,
                "data_type": "RELATED_TOPICS",
                "api_key": self.api_key
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            related_topics = results.get("related_topics", {})
            logger.info(f"Fetched related topics for '{query}' in {geo}")

            return related_topics

        except Exception as e:
            logger.error(f"Error fetching related topics: {str(e)}")
            return {"rising": [], "top": []}

    def get_related_queries(
        self,
        query: str,
        geo: str = "US",
        date: str = "today 12-m"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch related queries for a specific query.

        Args:
            query: Search query to analyze
            geo: Geographic location code (e.g., 'US', 'LK', 'IN')
            date: Time period (e.g., 'today 12-m', 'today 3-m', 'today 1-m')

        Returns:
            Dictionary with 'rising' and 'top' lists of related queries
        """
        try:
            params = {
                "engine": "google_trends",
                "q": query,
                "geo": geo,
                "date": date,
                "data_type": "RELATED_QUERIES",
                "api_key": self.api_key
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            related_queries = results.get("related_queries", {})
            logger.info(f"Fetched related queries for '{query}' in {geo}")

            return related_queries

        except Exception as e:
            logger.error(f"Error fetching related queries: {str(e)}")
            return {"rising": [], "top": []}

    def get_interest_by_region(
        self,
        query: str,
        geo: str = "",
        region_level: str = "COUNTRY",
        date: str = "today 12-m"
    ) -> List[Dict[str, Any]]:
        """
        Fetch interest by region for a specific query.

        Args:
            query: Search query to analyze
            geo: Geographic location code (e.g., '', 'US', 'LK', 'LK-1')
                 - Empty string for worldwide country-level data
                 - Country code (e.g., 'LK') for region-level data (provinces/states)
                 - Region code (e.g., 'LK-1') for city-level data
            region_level: Level of regional detail
                 - 'COUNTRY': Worldwide countries (geo should be empty)
                 - 'REGION': Provinces/States within a country (geo = country code)
                 - 'CITY': Cities within a region (geo = region code like 'LK-1')
            date: Time period (e.g., 'today 12-m', 'today 3-m', 'today 1-m')

        Returns:
            List of regions with interest values
        """
        try:
            params = {
                "engine": "google_trends",
                "q": query,
                "geo": geo,
                "date": date,
                "data_type": "GEO_MAP_0",
                "api_key": self.api_key
            }

            # Add region parameter for REGION or CITY level
            if region_level in ["REGION", "CITY"]:
                params["region"] = region_level

            search = GoogleSearch(params)
            results = search.get_dict()

            interest_by_region = results.get("interest_by_region", [])
            logger.info(f"Fetched interest by region for '{query}' in {geo} at {region_level} level")

            return interest_by_region

        except Exception as e:
            logger.error(f"Error fetching interest by region: {str(e)}")
            return []

    def get_complete_details(
        self,
        query: str,
        geo: str = "US",
        date: str = "today 12-m",
        include_region_drill_down: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch all detailed information for a specific query.

        Args:
            query: Search query to analyze
            geo: Geographic location code (e.g., 'US', 'LK', 'IN')
            date: Time period (e.g., 'today 12-m', 'today 3-m', 'today 1-m')
            include_region_drill_down: If True, fetches region-level and city-level data

        Returns:
            Dictionary with all detailed information
        """
        try:
            # Fetch all data types in parallel (conceptually)
            interest_over_time = self.get_interest_over_time(query, geo, date)
            related_topics = self.get_related_topics(query, geo, date)
            related_queries = self.get_related_queries(query, geo, date)

            # For interest by region, start with country-level if no geo specified
            # Otherwise start with region-level (provinces/states)
            if not geo or geo == "":
                # Worldwide country-level data
                interest_by_region = self.get_interest_by_region(query, "", "COUNTRY", date)
                region_drill_down = None
            else:
                # Region-level data for the specified country
                interest_by_region = self.get_interest_by_region(query, geo, "REGION", date)

                # Optional: fetch city-level data for each region
                region_drill_down = None
                if include_region_drill_down and interest_by_region:
                    region_drill_down = {}
                    # Fetch city data for top 3 regions only to avoid too many API calls
                    for region in interest_by_region[:3]:
                        region_geo = region.get('geo')
                        if region_geo:
                            cities = self.get_interest_by_region(query, region_geo, "CITY", date)
                            region_drill_down[region_geo] = {
                                "location": region.get('location'),
                                "cities": cities
                            }

            result = {
                "query": query,
                "geo": geo,
                "date": date,
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "interest_over_time": interest_over_time,
                "related_topics": related_topics,
                "related_queries": related_queries,
                "interest_by_region": interest_by_region,
                "region_drill_down": region_drill_down
            }

            logger.info(f"Fetched complete details for '{query}' in {geo}")
            return result

        except Exception as e:
            logger.error(f"Error fetching complete details: {str(e)}")
            return {
                "query": query,
                "geo": geo,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }
