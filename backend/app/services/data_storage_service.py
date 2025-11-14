from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import uuid
from ..database import (
    get_google_trends_collection,
    get_youtube_collection,
    get_tiktok_collection,
    get_unified_trends_collection
)

logger = logging.getLogger(__name__)


class DataStorageService:
    """Service for storing and retrieving trending data from MongoDB"""

    def __init__(self):
        pass

    async def store_google_trends_item(
        self,
        query: str,
        country_code: str,
        trend_data: Dict[str, Any],
        user_id: str
    ) -> bool:
        """
        Store or update a Google Trends item in MongoDB.
        This method MERGES new data with existing data instead of replacing it.

        Args:
            query: The search query
            country_code: Country code
            trend_data: The trending data to store
            user_id: User ID from authentication token

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = get_google_trends_collection()

            # Check if document exists for this user
            existing_doc = await collection.find_one({
                "query": query,
                "country_code": country_code,
                "user_id": user_id
            })

            # Start with existing document or create new one
            if existing_doc:
                # Remove MongoDB _id for easier manipulation
                doc_id = existing_doc["_id"]
                document = existing_doc.copy()
            else:
                doc_id = str(uuid.uuid4())
                document = {
                    "_id": doc_id,
                    "query": query,
                    "country_code": country_code,
                    "user_id": user_id,
                    "created_at": datetime.utcnow()
                }

            # Update only fields that are present and not None in trend_data
            # Basic trending fields (from /google-trends endpoint)
            if trend_data.get("search_volume") is not None:
                document["search_volume"] = trend_data.get("search_volume")
            if trend_data.get("increase_percentage") is not None:
                document["increase_percentage"] = trend_data.get("increase_percentage")
            if trend_data.get("active") is not None:
                document["active"] = trend_data.get("active")
            if trend_data.get("categories") is not None:
                document["categories"] = trend_data.get("categories")
            if trend_data.get("started_ago") is not None:
                document["started_ago"] = trend_data.get("started_ago")
            if trend_data.get("start_timestamp") is not None:
                document["start_timestamp"] = trend_data.get("start_timestamp")
            if trend_data.get("end_timestamp") is not None:
                document["end_timestamp"] = trend_data.get("end_timestamp")

            # Detailed data fields (from /google-trends/details endpoint)
            if trend_data.get("interest_over_time") is not None:
                document["interest_over_time"] = trend_data.get("interest_over_time")
            if trend_data.get("related_topics") is not None:
                document["related_topics"] = trend_data.get("related_topics")
            if trend_data.get("related_queries") is not None:
                document["related_queries"] = trend_data.get("related_queries")
            if trend_data.get("interest_by_region") is not None:
                document["interest_by_region"] = trend_data.get("interest_by_region")

            # Special handling for region_drill_down - merge instead of replace
            if trend_data.get("region_drill_down") is not None:
                if "region_drill_down" not in document or document["region_drill_down"] is None:
                    document["region_drill_down"] = {}
                # Merge new region drill-down data with existing
                document["region_drill_down"].update(trend_data.get("region_drill_down"))

            # Always update timestamp
            document["updated_at"] = datetime.utcnow()

            # Upsert (update if exists, insert if not)
            await collection.replace_one(
                {"_id": doc_id},
                document,
                upsert=True
            )

            logger.info(f"Stored/Updated Google Trends item: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing Google Trends item: {str(e)}")
            return False

    async def store_youtube_video(
        self,
        video_id: str,
        country_code: str,
        video_data: Dict[str, Any],
        user_id: str
    ) -> bool:
        """
        Store or update a YouTube video in MongoDB.
        This method MERGES new data with existing data instead of replacing it.

        Args:
            video_id: YouTube video ID
            country_code: Country code where it's trending
            video_data: The video data to store
            user_id: User ID from authentication token

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = get_youtube_collection()

            # Check if document exists for this user
            existing_doc = await collection.find_one({
                "video_id": video_id,
                "country_code": country_code,
                "user_id": user_id
            })

            # Start with existing document or create new one
            if existing_doc:
                doc_id = existing_doc["_id"]
                document = existing_doc.copy()
            else:
                doc_id = str(uuid.uuid4())
                document = {
                    "_id": doc_id,
                    "video_id": video_id,
                    "country_code": country_code,
                    "user_id": user_id,
                    "created_at": datetime.utcnow()
                }

            # Update only fields that are present and not None in video_data
            # Handle both camelCase (from trending API) and snake_case (from details API)

            # Basic video fields (from /youtube-trends endpoint)
            if video_data.get("title") is not None:
                document["title"] = video_data.get("title")
            if video_data.get("description") is not None:
                document["description"] = video_data.get("description")

            channel_id = video_data.get("channelId") or video_data.get("channel_id")
            if channel_id is not None:
                document["channel_id"] = channel_id

            channel_title = video_data.get("channelTitle") or video_data.get("channel_title")
            if channel_title is not None:
                document["channel_title"] = channel_title

            published_at = video_data.get("publishedAt") or video_data.get("published_at")
            if published_at is not None:
                document["published_at"] = published_at

            thumbnail_url = video_data.get("thumbnail_url_standard") or video_data.get("thumbnail_url") or video_data.get("thumbnail")
            if thumbnail_url is not None:
                document["thumbnail_url"] = thumbnail_url

            view_count = video_data.get("viewCount") or video_data.get("view_count")
            if view_count is not None:
                document["view_count"] = view_count

            like_count = video_data.get("likeCount") or video_data.get("like_count")
            if like_count is not None:
                document["like_count"] = like_count

            comment_count = video_data.get("commentCount") or video_data.get("comment_count")
            if comment_count is not None:
                document["comment_count"] = comment_count

            favorite_count = video_data.get("favoriteCount") or video_data.get("favorite_count")
            if favorite_count is not None:
                document["favorite_count"] = favorite_count

            if video_data.get("duration_sec") is not None:
                document["duration_sec"] = video_data.get("duration_sec")
            if video_data.get("tags") is not None:
                document["tags"] = video_data.get("tags")

            category_id = video_data.get("categoryId") or video_data.get("category_id")
            if category_id is not None:
                document["category_id"] = category_id

            default_language = video_data.get("defaultLanguage") or video_data.get("default_language")
            if default_language is not None:
                document["default_language"] = default_language

            if video_data.get("dimension") is not None:
                document["dimension"] = video_data.get("dimension")
            if video_data.get("definition") is not None:
                document["definition"] = video_data.get("definition")
            if video_data.get("caption") is not None:
                document["caption"] = video_data.get("caption")

            licensed_content = video_data.get("licensedContent") or video_data.get("licensed_content")
            if licensed_content is not None:
                document["licensed_content"] = licensed_content

            # Detailed data fields (from /youtube/details endpoint)
            if video_data.get("snippet") is not None:
                document["snippet"] = video_data.get("snippet")
            if video_data.get("content_details") is not None:
                document["content_details"] = video_data.get("content_details")
            if video_data.get("statistics") is not None:
                document["statistics"] = video_data.get("statistics")
            if video_data.get("status") is not None:
                document["status"] = video_data.get("status")
            if video_data.get("topic_details") is not None:
                document["topic_details"] = video_data.get("topic_details")
            if video_data.get("player") is not None:
                document["player"] = video_data.get("player")
            if video_data.get("recording_details") is not None:
                document["recording_details"] = video_data.get("recording_details")
            if video_data.get("available_localizations") is not None:
                document["available_localizations"] = video_data.get("available_localizations")
            if video_data.get("comments") is not None:
                document["comments"] = video_data.get("comments")

            # Always update timestamp
            document["updated_at"] = datetime.utcnow()

            # Upsert
            await collection.replace_one(
                {"_id": doc_id},
                document,
                upsert=True
            )

            logger.info(f"Stored/Updated YouTube video: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing YouTube video: {str(e)}")
            return False

    async def store_tiktok_item(
        self,
        item_type: str,
        name: str,
        country_code: str,
        item_data: Dict[str, Any],
        user_id: str
    ) -> bool:
        """
        Store or update a TikTok item in MongoDB.
        This method MERGES new data with existing data instead of replacing it.

        Args:
            item_type: Type of item (hashtag, creator, sound, video)
            name: Name/title of the item
            country_code: Country code
            item_data: The item data to store
            user_id: User ID from authentication token

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = get_tiktok_collection()

            # Check if document exists for this user
            existing_doc = await collection.find_one({
                "item_type": item_type,
                "name": name,
                "country_code": country_code,
                "user_id": user_id
            })

            # Start with existing document or create new one
            if existing_doc:
                doc_id = existing_doc["_id"]
                document = existing_doc.copy()
            else:
                doc_id = str(uuid.uuid4())
                document = {
                    "_id": doc_id,
                    "item_type": item_type,
                    "name": name,
                    "country_code": country_code,
                    "user_id": user_id,
                    "created_at": datetime.utcnow()
                }

            # Update common fields if present
            if item_data.get("url") is not None:
                document["url"] = item_data.get("url")
            if item_data.get("rank") is not None:
                document["rank"] = item_data.get("rank")

            # Add/update type-specific fields
            if item_type == "hashtag":
                if item_data.get("videoCount") is not None:
                    document["video_count"] = item_data.get("videoCount")
                if item_data.get("viewCount") is not None:
                    document["view_count"] = item_data.get("viewCount")
                if item_data.get("industryName") is not None:
                    document["industry_name"] = item_data.get("industryName")
                if item_data.get("trendingHistogram") is not None:
                    document["trending_histogram"] = item_data.get("trendingHistogram")
                if item_data.get("relatedCreators") is not None:
                    document["related_creators"] = item_data.get("relatedCreators")

            elif item_type == "creator":
                if item_data.get("followerCount") is not None:
                    document["follower_count"] = item_data.get("followerCount")
                if item_data.get("likedCount") is not None:
                    document["liked_count"] = item_data.get("likedCount")
                if item_data.get("avatar") is not None:
                    document["avatar"] = item_data.get("avatar")
                if item_data.get("relatedVideos") is not None:
                    document["related_videos"] = item_data.get("relatedVideos")

            elif item_type == "sound":
                if item_data.get("author") is not None:
                    document["author"] = item_data.get("author")
                if item_data.get("durationSec") is not None:
                    document["duration_sec"] = item_data.get("durationSec")
                if item_data.get("coverUrl") is not None:
                    document["cover_url"] = item_data.get("coverUrl")
                if item_data.get("trendingHistogram") is not None:
                    document["trending_histogram"] = item_data.get("trendingHistogram")

            elif item_type == "video":
                if item_data.get("durationSec") is not None:
                    document["duration_sec"] = item_data.get("durationSec")
                if item_data.get("coverUrl") is not None:
                    document["cover_url"] = item_data.get("coverUrl")

            # Always update timestamp
            document["updated_at"] = datetime.utcnow()

            # Upsert
            await collection.replace_one(
                {"_id": doc_id},
                document,
                upsert=True
            )

            logger.info(f"Stored/Updated TikTok {item_type}: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing TikTok item: {str(e)}")
            return False

    async def store_batch_items(
        self,
        platform: str,
        items: List[Dict[str, Any]],
        country_code: str
    ) -> Dict[str, int]:
        """
        Store multiple items from a platform in batch.

        Args:
            platform: Platform name ('google_trends', 'youtube', 'tiktok')
            items: List of items to store
            country_code: Country code

        Returns:
            Dictionary with success/failure counts
        """
        success_count = 0
        failure_count = 0

        try:
            if platform == "google_trends":
                for item in items:
                    query = item.get("query") or item.get("name")
                    if query:
                        success = await self.store_google_trends_item(query, country_code, item)
                        if success:
                            success_count += 1
                        else:
                            failure_count += 1

            elif platform == "youtube":
                for item in items:
                    video_id = item.get("id")
                    if video_id:
                        success = await self.store_youtube_video(video_id, country_code, item)
                        if success:
                            success_count += 1
                        else:
                            failure_count += 1

            elif platform == "tiktok":
                for item in items:
                    item_type = item.get("type", "").lower()
                    name = item.get("name")
                    if item_type and name:
                        success = await self.store_tiktok_item(item_type, name, country_code, item)
                        if success:
                            success_count += 1
                        else:
                            failure_count += 1

            logger.info(f"Stored {success_count} items from {platform}, {failure_count} failures")

        except Exception as e:
            logger.error(f"Error in batch storage: {str(e)}")

        return {
            "success": success_count,
            "failure": failure_count,
            "total": success_count + failure_count
        }

    async def get_google_trends_item(
        self,
        query: str,
        country_code: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a Google Trends item from MongoDB.

        Args:
            query: The search query
            country_code: Country code
            user_id: User ID from authentication token

        Returns:
            Item document or None if not found
        """
        try:
            collection = get_google_trends_collection()

            document = await collection.find_one({
                "query": query,
                "country_code": country_code,
                "user_id": user_id
            })
            if document:
                # Remove MongoDB _id field
                document.pop("_id", None)
                return document

            return None

        except Exception as e:
            logger.error(f"Error retrieving Google Trends item: {str(e)}")
            return None

    async def get_youtube_video(
        self,
        video_id: str,
        country_code: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a YouTube video from MongoDB.

        Args:
            video_id: YouTube video ID
            country_code: Country code
            user_id: User ID from authentication token

        Returns:
            Video document or None if not found
        """
        try:
            collection = get_youtube_collection()

            document = await collection.find_one({
                "video_id": video_id,
                "country_code": country_code,
                "user_id": user_id
            })
            if document:
                # Remove MongoDB _id field
                document.pop("_id", None)
                return document

            return None

        except Exception as e:
            logger.error(f"Error retrieving YouTube video: {str(e)}")
            return None

    async def get_tiktok_item(
        self,
        item_type: str,
        name: str,
        country_code: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a TikTok item from MongoDB.

        Args:
            item_type: Type of item (hashtag, creator, sound, video)
            name: Name/title of the item
            country_code: Country code
            user_id: User ID from authentication token

        Returns:
            Item document or None if not found
        """
        try:
            collection = get_tiktok_collection()

            document = await collection.find_one({
                "item_type": item_type,
                "name": name,
                "country_code": country_code,
                "user_id": user_id
            })
            if document:
                # Remove MongoDB _id field
                document.pop("_id", None)
                return document

            return None

        except Exception as e:
            logger.error(f"Error retrieving TikTok item: {str(e)}")
            return None

    async def store_unified_trends(
        self,
        country_code: str,
        category: Optional[str],
        time_range: str,
        trends_data: List[Dict[str, Any]],
        user_id: str
    ) -> bool:
        """
        Store unified trending data in MongoDB.
        Each request creates a new snapshot with timestamp.

        Args:
            country_code: Country code
            category: Category filter (can be None)
            time_range: Time range filter
            trends_data: List of trending items with scores
            user_id: User ID from authentication token

        Returns:
            True if successful, False otherwise
        """
        try:
            collection = get_unified_trends_collection()

            document = {
                "_id": str(uuid.uuid4()),
                "user_id": user_id,
                "country_code": country_code,
                "category": category,
                "time_range": time_range,
                "trends": trends_data,
                "total_count": len(trends_data),
                "platform_counts": {
                    "google_trends": len([t for t in trends_data if t.get("platform") == "google_trends"]),
                    "youtube": len([t for t in trends_data if t.get("platform") == "youtube"]),
                    "tiktok": len([t for t in trends_data if t.get("platform") == "tiktok"])
                },
                "created_at": datetime.utcnow(),
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

            await collection.insert_one(document)
            logger.info(f"Stored unified trends snapshot: {document['_id']}")
            return True

        except Exception as e:
            logger.error(f"Error storing unified trends: {str(e)}")
            return False

    async def get_latest_unified_trends(
        self,
        country_code: str,
        user_id: str,
        category: Optional[str] = None,
        time_range: str = "7d"
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve the latest unified trends snapshot from MongoDB.

        Args:
            country_code: Country code
            user_id: User ID from authentication token
            category: Category filter (can be None)
            time_range: Time range filter

        Returns:
            Latest trends document or None if not found
        """
        try:
            collection = get_unified_trends_collection()

            query = {
                "user_id": user_id,
                "country_code": country_code,
                "time_range": time_range
            }

            # Add category to query only if it's not None
            if category is not None:
                query["category"] = category
            else:
                query["category"] = None

            # Find the most recent document matching the criteria
            document = await collection.find_one(
                query,
                sort=[("created_at", -1)]  # Sort by created_at descending
            )

            if document:
                # Remove MongoDB _id field
                document.pop("_id", None)
                return document

            return None

        except Exception as e:
            logger.error(f"Error retrieving latest unified trends: {str(e)}")
            return None
