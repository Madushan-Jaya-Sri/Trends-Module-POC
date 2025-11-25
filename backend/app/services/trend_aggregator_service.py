"""
Trend Aggregator Service

This service aggregates trending data from all platforms (Google Trends, YouTube, TikTok)
into a unified format for universal scoring and filtering.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from .trending_score_calculator import TrendingScoreCalculator

# Import service types for type checking only (avoids circular imports)
if TYPE_CHECKING:
    from .google_trends_service import GoogleTrendsService
    from .tiktok_service import TikTokService
    from .youtube_service import YouTubeService

logger = logging.getLogger(__name__)


class TrendAggregatorService:
    """
    Aggregates trending data from multiple platforms and normalizes it
    for unified scoring and analysis.
    """

    def __init__(
        self,
        google_service: 'GoogleTrendsService',
        tiktok_service: 'TikTokService',
        youtube_service: 'YouTubeService'
    ):
        self.google_service = google_service
        self.tiktok_service = tiktok_service
        self.youtube_service = youtube_service
        self.score_calculator = TrendingScoreCalculator()
    
    def aggregate_all_trends(
        self,
        country_code: str = "US",
        category: Optional[Any] = None,
        max_results: int = 10,
        time_period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch and aggregate trending data from all platforms with optimized pre-filtering.

        Args:
            country_code: Country code for regional trends
            category: Optional unified category filter
            max_results: Number of results to fetch per platform
            time_period: Time period filter ('24h', '7d', '30d', '90d')

        Returns:
            Dictionary containing all trends in normalized format
        """
        logger.info("=" * 80)
        logger.info(f"[AGGREGATOR] Starting trend aggregation")
        logger.info(f"[AGGREGATOR] Input parameters: country_code='{country_code}', category={category}, max_results={max_results}, time_period='{time_period}'")

        all_trends = []

        # Map time_period to platform-specific parameters
        google_hours = None
        youtube_days = None
        tiktok_days = None

        if time_period:
            if time_period == '24h':
                google_hours = 24  # Past 24 hours
                youtube_days = 1
                tiktok_days = 1  # Will fetch 7 days and filter to 1
            elif time_period == '7d':
                google_hours = 168  # Past 7 days
                youtube_days = 7
                tiktok_days = 7
            elif time_period == '30d':
                google_hours = 168  # Max 7 days for Google Trends
                youtube_days = 30
                tiktok_days = 30
            elif time_period == '90d':
                google_hours = 168  # Max 7 days for Google Trends
                youtube_days = 90
                tiktok_days = 90  # Will use 120 days range

        # Fetch from Google Trends
        try:
            logger.info(f"[PLATFORM API] Calling Google Trends API with: country_code='{country_code}', category={category}, hours={google_hours}")
            google_trends = self.google_service.get_trending_now(
                country_code=country_code,
                category=category,
                hours=google_hours
            )
            normalized_google = self._normalize_google_trends(google_trends)
            all_trends.extend(normalized_google)
            logger.info(f"[PLATFORM API] Google Trends returned {len(google_trends)} items → normalized to {len(normalized_google)} trends")
        except Exception as e:
            logger.error(f"[PLATFORM API] Error fetching Google Trends: {str(e)}")

        # Fetch from YouTube
        try:
            logger.info(f"[PLATFORM API] Calling YouTube API with: country_code='{country_code}', max_results={max_results}, category={category}, time_period_days={youtube_days}")
            youtube_videos = self.youtube_service.get_trending_videos(
                country_code=country_code,
                max_results=max_results,
                category=category,
                time_period_days=youtube_days
            )
            normalized_youtube = self._normalize_youtube_trends(youtube_videos)
            all_trends.extend(normalized_youtube)
            logger.info(f"[PLATFORM API] YouTube returned {len(youtube_videos)} items → normalized to {len(normalized_youtube)} trends")
        except Exception as e:
            logger.error(f"[PLATFORM API] Error fetching YouTube trends: {str(e)}")

        # Fetch from TikTok
        try:
            # Only pass category if it's not None (let TikTok use its default)
            tiktok_kwargs = {
                "country_code": country_code,
                "results_per_page": max_results,
                "time_period_days": tiktok_days
            }
            if category is not None:
                tiktok_kwargs["category"] = category

            logger.info(f"[PLATFORM API] Calling TikTok API with: {tiktok_kwargs}")
            tiktok_data = self.tiktok_service.get_trending_data(**tiktok_kwargs)
            normalized_tiktok = self._normalize_tiktok_trends(tiktok_data)
            all_trends.extend(normalized_tiktok)

            tiktok_counts = {
                'hashtags': len(tiktok_data.get('hashtags', [])),
                'creators': len(tiktok_data.get('creators', [])),
                'sounds': len(tiktok_data.get('sounds', [])),
                'videos': len(tiktok_data.get('videos', []))
            }
            logger.info(f"[PLATFORM API] TikTok returned {tiktok_counts} → normalized to {len(normalized_tiktok)} trends")
        except Exception as e:
            logger.error(f"[PLATFORM API] Error fetching TikTok trends: {str(e)}")

        return {
            'trends': all_trends,
            'total_count': len(all_trends),
            'platform_counts': {
                'google_trends': len([t for t in all_trends if t['platform'] == 'google_trends']),
                'youtube': len([t for t in all_trends if t['platform'] == 'youtube']),
                'tiktok': len([t for t in all_trends if t['platform'] == 'tiktok'])
            }
        }
    
    def _normalize_google_trends(self, trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize Google Trends data to unified format."""
        normalized = []
        
        for trend in trends:
            normalized.append({
                'platform': 'google_trends',
                'entity_type': 'search_query',
                'id': trend.get('query', ''),
                'query': trend.get('query', ''),
                'title': trend.get('query', ''),
                'name': trend.get('query', ''),
                'url': trend.get('serpapi_news_link', ''),
                'search_volume': trend.get('search_volume', 0),
                'increase_percentage': trend.get('increase_percentage', 0),
                'start_timestamp': trend.get('start_timestamp'),
                'active': trend.get('active', True),
                'categories': trend.get('categories', []),
                'trend_breakdown': trend.get('trend_breakdown', []),
                'started': trend.get('started', ''),
                'started_ago': trend.get('started_ago', ''),
                'raw_data': trend
            })
        
        return normalized
    
    def _normalize_youtube_trends(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize YouTube data to unified format."""
        normalized = []
        
        for video in videos:
            normalized.append({
                'platform': 'youtube',
                'entity_type': 'video',
                'id': video.get('id', ''),
                'title': video.get('title', ''),
                'name': video.get('title', ''),
                'url': f"https://www.youtube.com/watch?v={video.get('id', '')}",
                'thumbnail': video.get('thumbnail_url_standard', ''),
                'channelTitle': video.get('channelTitle', ''),
                'publishedAt': video.get('publishedAt', ''),
                'viewCount': video.get('viewCount', 0),
                'likeCount': video.get('likeCount', 0),
                'commentCount': video.get('commentCount', 0),
                'duration_sec': video.get('duration_sec', 0),
                'categoryId': video.get('categoryId', ''),
                'raw_data': video
            })
        
        return normalized
    
    def _normalize_tiktok_trends(self, tiktok_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Normalize TikTok data to unified format."""
        normalized = []
        
        # Normalize hashtags
        for hashtag in tiktok_data.get('hashtags', []):
            normalized.append({
                'platform': 'tiktok',
                'entity_type': 'hashtag',
                'id': hashtag.get('name', ''),
                'name': hashtag.get('name', ''),
                'title': f"#{hashtag.get('name', '')}",
                'url': hashtag.get('url', ''),
                'rank': hashtag.get('rank', 0),
                'viewCount': hashtag.get('viewCount', 0),
                'videoCount': hashtag.get('videoCount', 0),
                'industryName': hashtag.get('industryName', ''),
                'trendingHistogram': hashtag.get('trendingHistogram', []),
                'relatedCreators': hashtag.get('relatedCreators', []),
                'raw_data': hashtag
            })
        
        # Normalize creators
        for creator in tiktok_data.get('creators', []):
            normalized.append({
                'platform': 'tiktok',
                'entity_type': 'creator',
                'id': creator.get('url', ''),
                'name': creator.get('name', ''),
                'title': creator.get('name', ''),
                'url': creator.get('url', ''),
                'avatar': creator.get('avatar', ''),
                'rank': creator.get('rank', 0),
                'followerCount': creator.get('followerCount', 0),
                'likedCount': creator.get('likedCount', 0),
                'relatedVideos': creator.get('relatedVideos', []),
                'raw_data': creator
            })
        
        # Normalize sounds
        for sound in tiktok_data.get('sounds', []):
            normalized.append({
                'platform': 'tiktok',
                'entity_type': 'sound',
                'id': sound.get('url', ''),
                'name': sound.get('name', ''),
                'title': sound.get('name', ''),
                'url': sound.get('url', ''),
                'coverUrl': sound.get('coverUrl', ''),
                'rank': sound.get('rank', 0),
                'author': sound.get('author', ''),
                'durationSec': sound.get('durationSec', 0),
                'trendingHistogram': sound.get('trendingHistogram', []),
                'raw_data': sound
            })
        
        # Normalize videos
        for video in tiktok_data.get('videos', []):
            normalized.append({
                'platform': 'tiktok',
                'entity_type': 'video',
                'id': video.get('url', ''),
                'name': video.get('name', ''),
                'title': video.get('name', ''),
                'url': video.get('url', ''),
                'coverUrl': video.get('coverUrl', ''),
                'rank': video.get('rank', 0),
                'durationSec': video.get('durationSec', 0),
                'raw_data': video
            })
        
        return normalized
    
    def calculate_trending_scores(
        self,
        trends: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate universal trending scores for all items.
        
        Args:
            trends: List of normalized trends
            
        Returns:
            Trends with calculated scores, sorted by score
        """
        return self.score_calculator.calculate_universal_score_adaptive(trends)
    
    def filter_by_time_range(
        self,
        trends: List[Dict[str, Any]],
        time_range: str
    ) -> List[Dict[str, Any]]:
        """
        Filter trends by time range.
        
        Args:
            trends: List of trends to filter
            time_range: One of: '1h', '24h', '7d', '30d', '3m', '6m', '1y'
            
        Returns:
            Filtered list of trends
        """
        now = datetime.now(timezone.utc)
        
        # Parse time range
        time_delta_map = {
            '1h': timedelta(hours=1),
            '24h': timedelta(hours=24),
            '7d': timedelta(days=7),
            '30d': timedelta(days=30),
            '3m': timedelta(days=90),
            '6m': timedelta(days=180),
            '1y': timedelta(days=365)
        }
        
        if time_range not in time_delta_map:
            logger.warning(f"Invalid time range: {time_range}, returning all trends")
            return trends
        
        cutoff_time = now - time_delta_map[time_range]
        cutoff_timestamp = cutoff_time.timestamp()
        
        filtered = []
        
        for trend in trends:
            platform = trend.get('platform', '')
            
            # Get timestamp based on platform
            timestamp = None
            
            if platform == 'google_trends':
                timestamp = trend.get('start_timestamp')
            elif platform == 'youtube':
                published_at = trend.get('publishedAt', '')
                if published_at:
                    try:
                        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        timestamp = dt.timestamp()
                    except:
                        pass
            elif platform == 'tiktok':
                # TikTok uses trending histogram
                histogram = trend.get('trendingHistogram', [])
                if histogram:
                    try:
                        date_str = histogram[-1].get('date', '')
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        timestamp = dt.timestamp()
                    except:
                        pass
            
            # Include if within time range (or no timestamp available - assume recent)
            if timestamp is None or timestamp >= cutoff_timestamp:
                filtered.append(trend)
        
        logger.info(f"Filtered {len(filtered)}/{len(trends)} trends within {time_range}")
        return filtered