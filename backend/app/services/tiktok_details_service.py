from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TikTokDetailsService:
    """Service for organizing and enhancing TikTok item details"""

    def __init__(self):
        pass

    def get_hashtag_details(self, hashtag_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed information for a TikTok hashtag.

        Args:
            hashtag_data: Raw hashtag data from TikTok service or MongoDB

        Returns:
            Dictionary with organized hashtag details
        """
        try:
            # Handle both camelCase (from API) and snake_case (from MongoDB)
            details = {
                "item_type": "hashtag",
                "name": hashtag_data.get("name"),
                "url": hashtag_data.get("url"),
                "country_code": hashtag_data.get("countryCode") or hashtag_data.get("country_code"),
                "rank": hashtag_data.get("rank"),

                # Engagement metrics
                "metrics": {
                    "video_count": hashtag_data.get("videoCount") or hashtag_data.get("video_count", 0),
                    "view_count": hashtag_data.get("viewCount") or hashtag_data.get("view_count", 0),
                },

                # Industry classification
                "industry": {
                    "name": hashtag_data.get("industryName") or hashtag_data.get("industry_name"),
                },

                # Trending data
                "trending_histogram": hashtag_data.get("trendingHistogram") or hashtag_data.get("trending_histogram", []),

                # Related creators
                "related_creators": hashtag_data.get("relatedCreators") or hashtag_data.get("related_creators", []),

                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

            logger.info(f"Organized details for hashtag: {hashtag_data.get('name')}")
            return details

        except Exception as e:
            logger.error(f"Error organizing hashtag details: {str(e)}")
            return {
                "error": str(e),
                "item_type": "hashtag",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

    def get_creator_details(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed information for a TikTok creator.

        Args:
            creator_data: Raw creator data from TikTok service or MongoDB

        Returns:
            Dictionary with organized creator details
        """
        try:
            # Handle both camelCase (from API) and snake_case (from MongoDB)
            details = {
                "item_type": "creator",
                "name": creator_data.get("name"),
                "url": creator_data.get("url"),
                "avatar": creator_data.get("avatar"),
                "country_code": creator_data.get("countryCode") or creator_data.get("country_code"),
                "rank": creator_data.get("rank"),

                # Engagement metrics
                "metrics": {
                    "follower_count": creator_data.get("followerCount") or creator_data.get("follower_count", 0),
                    "total_likes": creator_data.get("likedCount") or creator_data.get("liked_count", 0),
                },

                # Related videos
                "related_videos": creator_data.get("relatedVideos") or creator_data.get("related_videos", []),

                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

            logger.info(f"Organized details for creator: {creator_data.get('name')}")
            return details

        except Exception as e:
            logger.error(f"Error organizing creator details: {str(e)}")
            return {
                "error": str(e),
                "item_type": "creator",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

    def get_sound_details(self, sound_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed information for a TikTok sound.

        Args:
            sound_data: Raw sound data from TikTok service or MongoDB

        Returns:
            Dictionary with organized sound details
        """
        try:
            # Handle both camelCase (from API) and snake_case (from MongoDB)
            details = {
                "item_type": "sound",
                "name": sound_data.get("name"),
                "url": sound_data.get("url"),
                "cover_url": sound_data.get("coverUrl") or sound_data.get("cover_url"),
                "country_code": sound_data.get("countryCode") or sound_data.get("country_code"),
                "rank": sound_data.get("rank"),

                # Sound metadata
                "metadata": {
                    "author": sound_data.get("author"),
                    "duration_seconds": sound_data.get("durationSec") or sound_data.get("duration_sec", 0),
                },

                # Trending data
                "trending_histogram": sound_data.get("trendingHistogram") or sound_data.get("trending_histogram", []),

                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

            logger.info(f"Organized details for sound: {sound_data.get('name')}")
            return details

        except Exception as e:
            logger.error(f"Error organizing sound details: {str(e)}")
            return {
                "error": str(e),
                "item_type": "sound",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

    def get_video_details(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed information for a TikTok video.

        Args:
            video_data: Raw video data from TikTok service or MongoDB

        Returns:
            Dictionary with organized video details
        """
        try:
            # Handle both camelCase (from API) and snake_case (from MongoDB)
            details = {
                "item_type": "video",
                "name": video_data.get("name"),
                "url": video_data.get("url"),
                "cover_url": video_data.get("coverUrl") or video_data.get("cover_url"),
                "country_code": video_data.get("countryCode") or video_data.get("country_code"),
                "rank": video_data.get("rank"),

                # Video metadata
                "metadata": {
                    "duration_seconds": video_data.get("durationSec") or video_data.get("duration_sec", 0),
                },

                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

            logger.info(f"Organized details for video: {video_data.get('name')}")
            return details

        except Exception as e:
            logger.error(f"Error organizing video details: {str(e)}")
            return {
                "error": str(e),
                "item_type": "video",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

    def get_item_details(
        self,
        item_data: Dict[str, Any],
        item_type: str
    ) -> Dict[str, Any]:
        """
        Get detailed information for any TikTok item based on type.

        Args:
            item_data: Raw item data from TikTok service
            item_type: Type of item ('hashtag', 'creator', 'sound', 'video')

        Returns:
            Dictionary with organized item details
        """
        try:
            if item_type == "hashtag":
                return self.get_hashtag_details(item_data)
            elif item_type == "creator":
                return self.get_creator_details(item_data)
            elif item_type == "sound":
                return self.get_sound_details(item_data)
            elif item_type == "video":
                return self.get_video_details(item_data)
            else:
                logger.warning(f"Unknown TikTok item type: {item_type}")
                return {
                    "error": f"Unknown item type: {item_type}",
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }

        except Exception as e:
            logger.error(f"Error getting item details: {str(e)}")
            return {
                "error": str(e),
                "item_type": item_type,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }
