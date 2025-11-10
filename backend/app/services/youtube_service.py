from googleapiclient.discovery import build
from typing import List, Dict, Any, Optional
import logging
import isodate
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
        category: Optional[UnifiedCategory] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch trending videos from YouTube for a specific region.

        Args:
            country_code: Two-letter country code (e.g., 'US', 'MY', 'IN')
            max_results: Maximum number of videos to fetch (default: 10)
            category: Optional unified category to filter videos

        Returns:
            List of trending videos with comprehensive metadata
        """
        try:
            # Build request parameters
            request_params = {
                "part": "snippet,statistics,contentDetails",
                "chart": "mostPopular",
                "regionCode": country_code,
                "maxResults": max_results
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
