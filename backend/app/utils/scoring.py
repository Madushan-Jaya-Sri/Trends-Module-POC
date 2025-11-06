import statistics
from datetime import datetime
from typing import Dict, List, Any
import re
import logging

logger = logging.getLogger(__name__)


def calculate_youtube_score(video: Dict[str, Any]) -> float:
    """
    Calculate trending score for a YouTube video
    Score range: 0-100
    """
    try:
        # Calculate hours since upload
        published_at = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
        hours_since_upload = (datetime.now(published_at.tzinfo) - published_at).total_seconds() / 3600
        
        # 1. Engagement Rate (40% weight)
        views = video.get('views', 1)
        likes = video.get('likes', 0)
        comments = video.get('comments', 0)
        engagement_rate = (likes + comments) / max(views, 1)
        engagement_score = min(engagement_rate * 1000, 40)
        
        # 2. View Velocity (30% weight)
        views_per_hour = views / max(hours_since_upload, 1)
        velocity_score = min((views_per_hour / 10000) * 30, 30)
        
        # 3. Absolute Popularity (20% weight)
        popularity_score = min((views / 1000000) * 20, 20)
        
        # 4. Recency Bonus (10% weight)
        if hours_since_upload <= 24:
            recency_score = 10
        elif hours_since_upload <= 48:
            recency_score = 7
        elif hours_since_upload <= 72:
            recency_score = 4
        else:
            recency_score = 0
        
        total_score = engagement_score + velocity_score + popularity_score + recency_score
        return min(total_score, 100)
        
    except Exception as e:
        logger.error(f"Error calculating YouTube score: {str(e)}")
        return 50.0  # Default score


def calculate_tiktok_score(item: Dict[str, Any], item_type: str = "hashtag") -> float:
    """
    Calculate trending score for TikTok content
    Score range: 0-100
    """
    try:
        if item_type == "hashtag":
            # For hashtags
            views = item.get('viewCount', 0)
            video_count = item.get('videoCount', 1)
            rank = item.get('rank', 999)
            
            # 1. View score (50% weight)
            view_score = min((views / 10000000) * 50, 50)  # 10M views = full score
            
            # 2. Rank score (30% weight)
            rank_score = max(30 - (rank * 0.3), 0)
            
            # 3. Activity score (20% weight)
            activity_score = min((video_count / 1000) * 20, 20)
            
            return min(view_score + rank_score + activity_score, 100)
            
        elif item_type == "video":
            views = item.get('viewCount', 0)
            likes = item.get('likeCount', 0)
            comments = item.get('commentCount', 0)
            shares = item.get('shareCount', 0)
            
            # 1. Engagement Rate (40% weight)
            total_engagements = likes + comments + (shares * 2)
            engagement_rate = total_engagements / max(views, 1)
            engagement_score = min(engagement_rate * 500, 40)
            
            # 2. Viral Velocity (35% weight)
            velocity_score = min((views / 1000000) * 35, 35)
            
            # 3. Share Rate (25% weight)
            share_rate = shares / max(views, 1)
            share_score = min(share_rate * 2500, 25)
            
            return min(engagement_score + velocity_score + share_score, 100)
        
        return 50.0
        
    except Exception as e:
        logger.error(f"Error calculating TikTok score: {str(e)}")
        return 50.0


def calculate_google_trends_score(trend: Dict[str, Any]) -> float:
    """
    Calculate trending score for Google Trends keyword
    Score range: 0-100
    """
    try:
        interest = trend.get('value', 0)
        trend_type = trend.get('type', 'top')
        
        # 1. Interest Score (60% weight)
        interest_score = min((interest / 100) * 60, 60)
        
        # 2. Trend Type Bonus (40% weight)
        if trend_type == 'rising':
            type_bonus = 40
        else:
            type_bonus = 20
        
        return min(interest_score + type_bonus, 100)
        
    except Exception as e:
        logger.error(f"Error calculating Google Trends score: {str(e)}")
        return 50.0


def normalize_topic(topic: str) -> str:
    """
    Normalize topics for matching across platforms
    """
    if not topic:
        return ""
    
    # Convert to lowercase
    topic = topic.lower().strip()
    
    # Remove special characters except spaces
    topic = re.sub(r'[^\w\s]', '', topic)
    
    # Remove extra spaces
    topic = ' '.join(topic.split())
    
    return topic


def calculate_unified_score(trend_data: Dict[str, Any]) -> float:
    """
    Calculate final unified score for a topic across all platforms
    
    Factors:
    1. Average platform score (50%)
    2. Cross-platform presence bonus (30%)
    3. Score consistency (10%)
    4. Peak score bonus (10%)
    """
    try:
        scores = trend_data.get('scores', [50])
        platforms = set(trend_data.get('platforms', []))
        
        if not scores:
            return 50.0
        
        # 1. Average Score (50% weight)
        avg_score = sum(scores) / len(scores)
        avg_component = (avg_score / 100) * 50
        
        # 2. Cross-Platform Bonus (30% weight)
        platform_count = len(platforms)
        if platform_count >= 3:
            cross_platform_bonus = 30
        elif platform_count == 2:
            cross_platform_bonus = 20
        else:
            cross_platform_bonus = 10
        
        # 3. Consistency Score (10% weight)
        if len(scores) > 1:
            try:
                variance = statistics.stdev(scores)
                consistency = max(10 - (variance / 10), 0)
            except:
                consistency = 5
        else:
            consistency = 5
        
        # 4. Peak Score Bonus (10% weight)
        peak_score = max(scores)
        peak_bonus = (peak_score / 100) * 10
        
        unified_score = avg_component + cross_platform_bonus + consistency + peak_bonus
        
        return min(unified_score, 100)
        
    except Exception as e:
        logger.error(f"Error calculating unified score: {str(e)}")
        return 50.0


def generate_trending_reason(trend_data: Dict[str, Any]) -> str:
    """
    Generate human-readable reason for why something is trending
    """
    try:
        platforms = set(trend_data.get('platforms', []))
        scores = trend_data.get('scores', [])
        avg_score = sum(scores) / len(scores) if scores else 50
        
        if len(platforms) >= 3:
            return f"Trending across all platforms with {avg_score:.0f}/100 average score"
        elif len(platforms) == 2:
            platform_names = ' and '.join(sorted(platforms))
            return f"Trending on {platform_names} with {avg_score:.0f}/100 score"
        elif len(platforms) == 1:
            platform = list(platforms)[0]
            return f"Highly trending on {platform} with {avg_score:.0f}/100 score"
        else:
            return "Trending content"
            
    except Exception as e:
        logger.error(f"Error generating trending reason: {str(e)}")
        return "Trending content"