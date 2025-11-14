from googleapiclient.discovery import build
from typing import List, Dict, Any, Optional
import logging
import isodate
from datetime import datetime, timezone, timedelta
from ..constants import UnifiedCategory, get_youtube_category_string

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for fetching YouTube trending videos"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_trending_videos(
        self,
        country_code: str = "US",
        max_results: int = 10,
        category: Optional[UnifiedCategory] = None,
        time_period_days: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch trending videos from YouTube for a specific region.

        Args:
            country_code: Two-letter country code (e.g., 'US', 'MY', 'IN')
            max_results: Maximum number of videos to fetch (default: 10)
            category: Optional unified category to filter videos
            time_period_days: Optional time period filter in days (1, 7, 30, 90)
                             This will adjust maxResults and filter after fetching

        Returns:
            List of trending videos with comprehensive metadata
        """
        try:
            # Adjust maxResults based on time period for better filtering
            fetch_max_results = max_results
            if time_period_days is not None:
                if time_period_days == 1:
                    fetch_max_results = max(20, max_results)
                elif time_period_days == 7:
                    fetch_max_results = max(30, max_results)
                elif time_period_days == 30:
                    fetch_max_results = max(50, max_results)
                elif time_period_days == 90:
                    fetch_max_results = max(100, max_results)
                logger.info(f"Adjusted maxResults to {fetch_max_results} for {time_period_days} day period")

            # Build request parameters
            request_params = {
                "part": "snippet,statistics,contentDetails",
                "chart": "mostPopular",
                "regionCode": country_code,
                "maxResults": min(fetch_max_results, 200)  # YouTube API limit is 200
            }

            # Add category filter if provided
            if category:
                category_ids = get_youtube_category_string(category)
                if category_ids:
                    request_params["videoCategoryId"] = category_ids
                    logger.info(f"Filtering YouTube videos by category: {category.value} (IDs: {category_ids})")
                else:
                    logger.warning(f"Category {category.value} not supported by YouTube, fetching all trending videos")

            request = self.youtube.videos().list(**request_params)
            response = request.execute()
            videos = self._extract_youtube_trends(response)

            # Filter by time period if specified
            if time_period_days is not None:
                videos = self._filter_by_time_period(videos, time_period_days)
                logger.info(f"Filtered to {len(videos)} videos within {time_period_days} days")

            logger.info(f"Fetched {len(videos)} trending YouTube videos for {country_code}")
            return videos

        except Exception as e:
            logger.error(f"Error fetching YouTube data: {str(e)}")
            return []

    def _extract_youtube_trends(self, response: Dict) -> List[Dict[str, Any]]:
        """
        Extract key attributes from YouTube API response for trend analysis.

        Args:
            response: Raw response from YouTube API

        Returns:
            List of videos with enhanced metadata
        """
        videos = []

        for item in response.get('items', []):
            snippet = item.get('snippet', {})
            content_details = item.get('contentDetails', {})
            stats = item.get('statistics', {})

            # Extract thumbnail URL (standard if available, fallback to high)
            thumbnails = snippet.get('thumbnails', {})
            thumbnail_url_standard = (
                thumbnails.get('standard', {}).get('url') or
                thumbnails.get('high', {}).get('url') or
                ''
            )

            # Duration: Convert ISO 8601 duration to seconds (e.g., 'PT3M22S' -> 202)
            try:
                duration_sec = int(
                    isodate.parse_duration(
                        content_details.get('duration', 'PT0S')
                    ).total_seconds()
                )
            except Exception:
                duration_sec = 0

            # Tags as list (or empty list)
            tags = snippet.get('tags', [])

            # Build the dictionary with all relevant attributes
            video_data = {
                # Core identifiers
                "kind": item.get('kind', ''),
                "id": item.get('id', ''),

                # Publishing and channel info
                "publishedAt": snippet.get('publishedAt', ''),
                "channelId": snippet.get('channelId', ''),
                "channelTitle": snippet.get('channelTitle', ''),

                # Content details
                "title": snippet.get('title', ''),
                "description": snippet.get('description', ''),
                "tags": tags,
                "categoryId": snippet.get('categoryId', ''),
                "defaultLanguage": snippet.get('defaultLanguage', '') or snippet.get('defaultAudioLanguage', ''),
                "liveBroadcastContent": snippet.get('liveBroadcastContent', 'none'),

                # Thumbnails and visuals (for UI)
                "thumbnail_url_standard": thumbnail_url_standard,

                # Video properties
                "duration_sec": duration_sec,
                "dimension": content_details.get('dimension', ''),
                "definition": content_details.get('definition', ''),
                "caption": content_details.get('caption', 'false') == 'true',
                "licensedContent": content_details.get('licensedContent', False),
                "projection": content_details.get('projection', ''),

                # Statistics for trends (convert to int for analysis)
                "viewCount": int(stats.get('viewCount', 0)),
                "likeCount": int(stats.get('likeCount', 0)),
                "favoriteCount": int(stats.get('favoriteCount', 0)),
                "commentCount": int(stats.get('commentCount', 0)),

                # Additional useful fields
                "localized_title": snippet.get('localized', {}).get('title', ''),
                "localized_description": snippet.get('localized', {}).get('description', ''),
                "etag": item.get('etag', '')
            }

            videos.append(video_data)

        return videos

    def _filter_by_time_period(self, videos: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
        """
        Filter videos by time period based on publishedAt timestamp.

        Args:
            videos: List of videos to filter
            days: Number of days to filter by

        Returns:
            Filtered list of videos within the time period
        """
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(days=days)

        filtered_videos = []
        for video in videos:
            published_at = video.get('publishedAt', '')
            if published_at:
                try:
                    # Parse ISO 8601 timestamp
                    published_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    if published_dt >= cutoff_time:
                        filtered_videos.append(video)
                except Exception as e:
                    logger.warning(f"Could not parse publishedAt timestamp: {published_at}, error: {str(e)}")
                    # Include videos with unparseable timestamps to be safe
                    filtered_videos.append(video)
            else:
                # Include videos without timestamp
                filtered_videos.append(video)

        return filtered_videos
