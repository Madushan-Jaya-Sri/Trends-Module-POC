from googleapiclient.discovery import build
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging
import isodate

logger = logging.getLogger(__name__)


class YouTubeDetailsService:
    """Service for fetching detailed YouTube video information using YouTube Data API v3"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Fetch comprehensive details for a specific YouTube video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with detailed video information
        """
        try:
            # Request all available parts for maximum detail
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics,status,topicDetails,player,localizations,recordingDetails',
                id=video_id
            )
            response = request.execute()

            if not response.get('items'):
                logger.warning(f"No video found with ID: {video_id}")
                return {
                    "error": "Video not found",
                    "video_id": video_id,
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }

            video = response['items'][0]

            # Extract and organize the data
            snippet = video.get('snippet', {})
            content_details = video.get('contentDetails', {})
            statistics = video.get('statistics', {})
            status = video.get('status', {})
            topic_details = video.get('topicDetails', {})
            player = video.get('player', {})
            localizations = video.get('localizations', {})
            recording_details = video.get('recordingDetails', {})

            # Parse duration
            duration_iso = content_details.get('duration', 'PT0S')
            try:
                duration_seconds = int(isodate.parse_duration(duration_iso).total_seconds())
            except Exception:
                duration_seconds = 0

            # Build detailed response
            result = {
                "video_id": video_id,
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "kind": video.get('kind'),
                "etag": video.get('etag'),

                # Snippet (basic info)
                "snippet": {
                    "published_at": snippet.get('publishedAt'),
                    "channel_id": snippet.get('channelId'),
                    "channel_title": snippet.get('channelTitle'),
                    "title": snippet.get('title'),
                    "description": snippet.get('description'),
                    "thumbnails": snippet.get('thumbnails', {}),
                    "tags": snippet.get('tags', []),
                    "category_id": snippet.get('categoryId'),
                    "live_broadcast_content": snippet.get('liveBroadcastContent'),
                    "default_language": snippet.get('defaultLanguage'),
                    "default_audio_language": snippet.get('defaultAudioLanguage'),
                    "localized": snippet.get('localized', {})
                },

                # Content Details
                "content_details": {
                    "duration": duration_iso,
                    "duration_seconds": duration_seconds,
                    "dimension": content_details.get('dimension'),
                    "definition": content_details.get('definition'),
                    "caption": content_details.get('caption') == 'true',
                    "licensed_content": content_details.get('licensedContent', False),
                    "projection": content_details.get('projection'),
                    "content_rating": content_details.get('contentRating', {}),
                    "has_custom_thumbnail": content_details.get('hasCustomThumbnail')
                },

                # Statistics
                "statistics": {
                    "view_count": int(statistics.get('viewCount', 0)),
                    "like_count": int(statistics.get('likeCount', 0)),
                    "dislike_count": int(statistics.get('dislikeCount', 0)),
                    "favorite_count": int(statistics.get('favoriteCount', 0)),
                    "comment_count": int(statistics.get('commentCount', 0))
                },

                # Status
                "status": {
                    "upload_status": status.get('uploadStatus'),
                    "privacy_status": status.get('privacyStatus'),
                    "license": status.get('license'),
                    "embeddable": status.get('embeddable'),
                    "public_stats_viewable": status.get('publicStatsViewable'),
                    "made_for_kids": status.get('madeForKids')
                },

                # Topic Details
                "topic_details": {
                    "topic_categories": topic_details.get('topicCategories', [])
                },

                # Player (embed HTML)
                "player": {
                    "embed_html": player.get('embedHtml'),
                    "embed_height": player.get('embedHeight'),
                    "embed_width": player.get('embedWidth')
                },

                # Recording Details
                "recording_details": recording_details if recording_details else None,

                # Localizations (available translations)
                "available_localizations": list(localizations.keys()) if localizations else []
            }

            logger.info(f"Fetched detailed information for video: {video_id}")
            return result

        except Exception as e:
            logger.error(f"Error fetching video details for {video_id}: {str(e)}")
            return {
                "error": str(e),
                "video_id": video_id,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

    def get_video_comments(
        self,
        video_id: str,
        max_results: int = 20,
        order: str = "relevance"
    ) -> Dict[str, Any]:
        """
        Fetch top comments for a specific YouTube video.

        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to fetch (default: 20, max: 100)
            order: Order of comments ('time', 'relevance') - default: 'relevance'

        Returns:
            Dictionary with comment threads
        """
        try:
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(max_results, 100),
                order=order,
                textFormat='plainText'
            )
            response = request.execute()

            comments = []
            for item in response.get('items', []):
                top_level_comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    "author": top_level_comment.get('authorDisplayName'),
                    "author_channel_url": top_level_comment.get('authorChannelUrl'),
                    "text": top_level_comment.get('textDisplay'),
                    "like_count": top_level_comment.get('likeCount', 0),
                    "published_at": top_level_comment.get('publishedAt'),
                    "updated_at": top_level_comment.get('updatedAt'),
                    "reply_count": item['snippet'].get('totalReplyCount', 0)
                })

            result = {
                "video_id": video_id,
                "total_results": response.get('pageInfo', {}).get('totalResults', 0),
                "comments": comments,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

            logger.info(f"Fetched {len(comments)} comments for video: {video_id}")
            return result

        except Exception as e:
            logger.error(f"Error fetching comments for {video_id}: {str(e)}")
            return {
                "error": str(e),
                "video_id": video_id,
                "comments": [],
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }

    def get_complete_details(
        self,
        video_id: str,
        include_comments: bool = False,
        max_comments: int = 20
    ) -> Dict[str, Any]:
        """
        Fetch all available details for a video, optionally including comments.

        Args:
            video_id: YouTube video ID
            include_comments: Whether to include comments
            max_comments: Maximum number of comments to fetch if include_comments is True

        Returns:
            Dictionary with comprehensive video details
        """
        try:
            # Get video details
            details = self.get_video_details(video_id)

            # Optionally get comments
            if include_comments and 'error' not in details:
                comments_data = self.get_video_comments(video_id, max_comments)
                details['comments'] = comments_data.get('comments', [])
                details['total_comments'] = comments_data.get('total_results', 0)

            return details

        except Exception as e:
            logger.error(f"Error fetching complete details for {video_id}: {str(e)}")
            return {
                "error": str(e),
                "video_id": video_id,
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }
