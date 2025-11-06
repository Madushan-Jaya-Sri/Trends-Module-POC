from googleapiclient.discovery import build
from typing import Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class YouTubeService:
    def __init__(self, api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    def get_trending_videos(self, region_code: str = "US", max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch trending YouTube videos for a specific region
        
        Args:
            region_code: Two-letter region code (e.g., 'US', 'GB', 'IN')
            max_results: Number of videos to fetch (max 50 per request)
            
        Returns:
            List of trending videos with metadata
        """
        try:
            logger.info(f"Fetching YouTube trending videos for region: {region_code}")
            
            request = self.youtube.videos().list(
                part="snippet,statistics,contentDetails",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=max_results
            )
            
            response = request.execute()
            
            videos = []
            for item in response.get('items', []):
                video_data = {
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'category': item['snippet'].get('categoryId', 'Unknown'),
                    'tags': item['snippet'].get('tags', []),
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'likes': int(item['statistics'].get('likeCount', 0)),
                    'comments': int(item['statistics'].get('commentCount', 0)),
                    'url': f"https://www.youtube.com/watch?v={item['id']}"
                }
                videos.append(video_data)
            
            logger.info(f"Fetched {len(videos)} trending YouTube videos")
            return videos
            
        except Exception as e:
            logger.error(f"Error fetching YouTube trends: {str(e)}")
            return []
    
    def extract_topics_from_youtube(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract topics and keywords from YouTube videos
        """
        topics = []
        
        for video in videos[:30]:  # Top 30 videos
            # Add title as topic
            topics.append({
                "topic": video['title'],
                "source": "video_title",
                "views": video['views'],
                "likes": video['likes'],
                "comments": video['comments'],
                "url": video['url'],
                "published_at": video['published_at']
            })
            
            # Add tags as topics
            for tag in video.get('tags', [])[:5]:  # Top 5 tags per video
                topics.append({
                    "topic": tag,
                    "source": "tag",
                    "views": video['views'],
                    "url": video['url']
                })
        
        return topics