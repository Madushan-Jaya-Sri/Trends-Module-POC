from serpapi import GoogleSearch
from datetime import datetime, timezone
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GoogleTrendsService:
    """Service for fetching Google Trends data using SerpAPI"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_trending_now(self, country_code: str = "US") -> List[Dict[str, Any]]:
        """
        Fetch trending searches from Google Trends for a specific country.

        Args:
            country_code: Two-letter country code (e.g., 'US', 'LK', 'IN')

        Returns:
            List of trending searches with enhanced metadata
        """
        try:
            params = {
                "engine": "google_trends_trending_now",
                "geo": country_code,
                "api_key": self.api_key
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            # Process the results to add human-readable timestamps
            trending_searches = results.get("trending_searches", [])
            processed_searches = self._process_trending_searches(trending_searches)

            logger.info(f"Fetched {len(processed_searches)} trending searches for {country_code}")
            return processed_searches

        except Exception as e:
            logger.error(f"Error fetching Google Trends data: {str(e)}")
            return []

    def _process_trending_searches(self, trends: List[Dict]) -> List[Dict[str, Any]]:
        """
        Process trending searches to add human-readable time information.

        Args:
            trends: Raw trending searches from API

        Returns:
            Enhanced trending searches with time metadata
        """
        now = datetime.now(timezone.utc)
        current_timestamp = int(now.timestamp())

        for trend in trends:
            start_ts = trend.get('start_timestamp')
            if start_ts:
                start_dt = datetime.fromtimestamp(start_ts, tz=timezone.utc)

                # Add human-readable start time
                trend['started'] = start_dt.strftime("%b %d, %I:%M %p UTC")

                # Calculate time since start
                time_since_start = current_timestamp - start_ts
                trend['started_ago'] = self._format_duration(time_since_start)

                # For inactive trends, compute duration
                if not trend.get('active', True):
                    end_ts = trend.get('end_timestamp')
                    if end_ts:
                        duration = end_ts - start_ts
                        trend['lasted_for'] = self._format_duration(duration)
                    else:
                        trend['lasted_for'] = "unknown"
                else:
                    trend['lasted_for'] = None

        return trends

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """
        Convert seconds to human-readable duration.

        Args:
            seconds: Duration in seconds

        Returns:
            Human-readable duration string (e.g., "2h 30m")
        """
        if seconds < 60:
            return f"{seconds} sec"

        mins = seconds // 60
        if mins < 60:
            return f"{mins} min"

        hours = mins // 60
        mins_rem = mins % 60
        if hours < 24:
            return f"{hours}h {mins_rem}m" if mins_rem else f"{hours}h"

        days = hours // 24
        hours_rem = hours % 24
        return f"{days}d {hours_rem}h" if hours_rem else f"{days}d"
