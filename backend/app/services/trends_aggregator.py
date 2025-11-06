from typing import Dict, List, Any
from datetime import datetime
import logging
from collections import defaultdict

from ..services.tiktok_service import TikTokService
from ..services.youtube_service import YouTubeService
from ..services.google_trends_service import GoogleTrendsService
from ..utils.keyword_extractor import KeywordExtractor
from ..utils.scoring import (
    calculate_youtube_score,
    calculate_tiktok_score,
    calculate_google_trends_score,
    normalize_topic,
    calculate_unified_score,
    generate_trending_reason
)

logger = logging.getLogger(__name__)


class TrendsAggregator:
    def __init__(self, apify_key: str, youtube_key: str, serpapi_key: str, openai_key: str = None):
        self.tiktok_service = TikTokService(apify_key)
        self.youtube_service = YouTubeService(youtube_key)
        self.google_trends_service = GoogleTrendsService(serpapi_key)
        self.keyword_extractor = KeywordExtractor(openai_key)
    
    def aggregate_trends(self, country: str = "US", top_n: int = 20) -> Dict[str, Any]:
        """
        Main method to aggregate trends from all platforms
        
        Args:
            country: Country code (e.g., 'US', 'GB', 'IN')
            top_n: Number of top trends to return
            
        Returns:
            Aggregated trending data with recommendations
        """
        logger.info(f"Starting trend aggregation for country: {country}")
        
        # 1. Fetch data from all platforms
        tiktok_data = self.tiktok_service.get_trending_data(country)
        youtube_videos = self.youtube_service.get_trending_videos(country)
        google_trends = self.google_trends_service.get_trending_now(country)
        
        # 2. Extract and score topics from each platform
        all_trends = defaultdict(lambda: {
            'platforms': [],
            'scores': [],
            'content': [],
            'total_score': 0,
            'platform_count': 0
        })
        
        # Process TikTok hashtags
        for hashtag in tiktok_data.get('hashtags', [])[:30]:
            score = calculate_tiktok_score(hashtag, 'hashtag')
            topic_name = hashtag.get('name', '').replace('#', '')
            
            if not topic_name:
                continue
            
            # Extract keywords from hashtag
            keywords = self.keyword_extractor.extract_keywords(topic_name, max_keywords=3)
            
            for keyword in keywords:
                topic_normalized = normalize_topic(keyword)
                
                if topic_normalized:
                    all_trends[topic_normalized]['platforms'].append('TikTok')
                    all_trends[topic_normalized]['scores'].append(score)
                    all_trends[topic_normalized]['content'].append({
                        'platform': 'TikTok',
                        'title': f"#{topic_name}",
                        'url': hashtag.get('url', ''),
                        'score': score,
                        'views': hashtag.get('viewCount', 0)
                    })
        
        # Process YouTube videos
        for video in youtube_videos[:30]:
            score = calculate_youtube_score(video)
            
            # Extract keywords from title
            keywords = self.keyword_extractor.extract_keywords(video['title'], max_keywords=3)
            
            for keyword in keywords:
                topic_normalized = normalize_topic(keyword)
                
                if topic_normalized:
                    all_trends[topic_normalized]['platforms'].append('YouTube')
                    all_trends[topic_normalized]['scores'].append(score)
                    all_trends[topic_normalized]['content'].append({
                        'platform': 'YouTube',
                        'title': video['title'][:100],
                        'url': video['url'],
                        'score': score,
                        'views': video['views']
                    })
        
        # Process Google Trends
        for trend in google_trends[:30]:
            score = calculate_google_trends_score(trend)
            query = trend.get('query', '')
            
            if not query:
                continue
            
            # Extract keywords from query
            keywords = self.keyword_extractor.extract_keywords(query, max_keywords=2)
            
            for keyword in keywords:
                topic_normalized = normalize_topic(keyword)
                
                if topic_normalized:
                    all_trends[topic_normalized]['platforms'].append('Google')
                    all_trends[topic_normalized]['scores'].append(score)
                    all_trends[topic_normalized]['content'].append({
                        'platform': 'Google',
                        'title': query,
                        'url': trend.get('link', ''),
                        'score': score,
                        'interest': trend.get('value', 0)
                    })
        
        # 3. Calculate unified scores
        for topic, data in all_trends.items():
            data['total_score'] = calculate_unified_score(data)
            data['platform_count'] = len(set(data['platforms']))
        
        # 4. Sort by unified score
        sorted_trends = sorted(
            all_trends.items(),
            key=lambda x: x[1]['total_score'],
            reverse=True
        )
        
        # 5. Format recommendations
        recommendations = []
        for rank, (topic, data) in enumerate(sorted_trends[:top_n], 1):
            # Get top 3 content pieces
            top_content = sorted(
                data['content'],
                key=lambda x: x.get('score', 0),
                reverse=True
            )[:3]
            
            recommendation = {
                'rank': rank,
                'topic': topic.title(),
                'score': round(data['total_score'], 2),
                'platforms': list(set(data['platforms'])),
                'platform_count': data['platform_count'],
                'trending_reason': generate_trending_reason(data),
                'top_content': [
                    {
                        'platform': content['platform'],
                        'title': content['title'],
                        'url': content.get('url'),
                        'score': round(content['score'], 2)
                    }
                    for content in top_content
                ]
            }
            
            recommendations.append(recommendation)
        
        result = {
            'country': country,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'total_trends': len(all_trends),
            'recommendations': recommendations
        }
        
        logger.info(f"Trend aggregation complete. Generated {len(recommendations)} recommendations")
        
        return result
    
    def get_platform_stats(self, country: str = "US") -> Dict[str, Any]:
        """
        Get statistics about each platform
        """
        logger.info(f"Fetching platform statistics for country: {country}")
        
        stats = {
            'tiktok': {'status': 'unknown', 'count': 0},
            'youtube': {'status': 'unknown', 'count': 0},
            'google_trends': {'status': 'unknown', 'count': 0}
        }
        
        try:
            tiktok_data = self.tiktok_service.get_trending_data(country)
            stats['tiktok']['status'] = 'success' if not tiktok_data.get('error') else 'error'
            stats['tiktok']['count'] = len(tiktok_data.get('hashtags', [])) + len(tiktok_data.get('videos', []))
        except Exception as e:
            logger.error(f"TikTok stats error: {str(e)}")
            stats['tiktok']['status'] = 'error'
        
        try:
            youtube_videos = self.youtube_service.get_trending_videos(country)
            stats['youtube']['status'] = 'success'
            stats['youtube']['count'] = len(youtube_videos)
        except Exception as e:
            logger.error(f"YouTube stats error: {str(e)}")
            stats['youtube']['status'] = 'error'
        
        try:
            google_trends = self.google_trends_service.get_trending_now(country)
            stats['google_trends']['status'] = 'success'
            stats['google_trends']['count'] = len(google_trends)
        except Exception as e:
            logger.error(f"Google Trends stats error: {str(e)}")
            stats['google_trends']['status'] = 'error'
        
        return stats