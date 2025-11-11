"""
Universal Trending Score Calculator

This module calculates a unified trending score for content across Google Trends,
YouTube, and TikTok platforms using scientifically justified weightages.

Scoring Methodology:
-------------------
The score is normalized to 0-100 scale and considers multiple dimensions:

1. VOLUME (30% weight) - Raw reach and visibility
   - Justification: Volume is the primary indicator of trend magnitude
   - Higher volume = more people engaged = stronger trend

2. ENGAGEMENT (25% weight) - Quality of interaction
   - Justification: High engagement indicates genuine interest, not just passive views
   - Likes, comments, shares show active participation

3. VELOCITY (20% weight) - Speed of growth
   - Justification: Fast-growing trends indicate emerging phenomena
   - Viral content spreads exponentially, not linearly

4. RECENCY (15% weight) - How recent the trend is
   - Justification: Recent trends are more relevant for real-time insights
   - Exponential decay ensures older trends don't dominate

5. CROSS-PLATFORM PRESENCE (10% weight) - Multi-platform validation
   - Justification: Trends appearing on multiple platforms are more significant
   - Reduces platform-specific bias and noise

Note on Normalization:
- All metrics are normalized using min-max scaling within the dataset
- This ensures fair comparison across platforms with different scales
- Scores are relative to the current trending dataset
"""

import math
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TrendingScoreCalculator:
    """
    Calculate universal trending scores for content across platforms.
    
    Weightages (must sum to 1.0):
    - VOLUME: 0.30 (30%) - Raw reach
    - ENGAGEMENT: 0.25 (25%) - Quality of interaction
    - VELOCITY: 0.20 (20%) - Growth speed
    - RECENCY: 0.15 (15%) - Time relevance
    - CROSS_PLATFORM: 0.10 (10%) - Multi-platform presence
    """
    
    # Weight constants
    WEIGHT_VOLUME = 0.30
    WEIGHT_ENGAGEMENT = 0.25
    WEIGHT_VELOCITY = 0.20
    WEIGHT_RECENCY = 0.15
    WEIGHT_CROSS_PLATFORM = 0.10
    
    # Recency decay parameters (exponential decay)
    RECENCY_HALF_LIFE_HOURS = 24  # Score halves every 24 hours
    
    def __init__(self):
        self.current_time = datetime.now(timezone.utc)
        
    def calculate_universal_score_adaptive(
        self,
        all_trends: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate universal trending scores with ADAPTIVE weights per platform.
        
        Platform-Specific Weights:
        
        Google Trends (limited metrics):
        - Volume: 35% (increased)
        - Engagement: 15% (decreased - only has increase_pct)
        - Velocity: 30% (increased - strength of Google Trends)
        - Recency: 15% (same)
        - Cross-Platform: 5% (decreased)
        
        YouTube (balanced metrics):
        - Volume: 30%
        - Engagement: 25%
        - Velocity: 20%
        - Recency: 15%
        - Cross-Platform: 10%
        
        TikTok (rich engagement):
        - Volume: 25% (decreased)
        - Engagement: 30% (increased - strength of TikTok)
        - Velocity: 20%
        - Recency: 15%
        - Cross-Platform: 10%
        """
        if not all_trends:
            return []
        
        # Calculate individual component scores
        for trend in all_trends:
            trend['volume_score'] = self._calculate_volume_score(trend)
            trend['engagement_score'] = self._calculate_engagement_score(trend)
            trend['velocity_score'] = self._calculate_velocity_score(trend)
            trend['recency_score'] = self._calculate_recency_score(trend)
            trend['cross_platform_score'] = self._calculate_cross_platform_score(trend, all_trends)
        
        # Normalize Google Trends engagement to match other platforms
        all_trends = self._normalize_engagement_scores(all_trends)
        
        # Normalize all component scores to 0-100 scale
        self._normalize_scores(all_trends, 'volume_score')
        self._normalize_scores(all_trends, 'engagement_score')
        self._normalize_scores(all_trends, 'velocity_score')
        
        # Calculate final weighted score with PLATFORM-SPECIFIC WEIGHTS
        for trend in all_trends:
            platform = trend.get('platform', '')
            
            # Choose weights based on platform
            if platform == 'google_trends':
                # Emphasize what Google Trends is good at
                weights = {
                    'volume': 0.35,      # Higher
                    'engagement': 0.15,  # Lower (limited data)
                    'velocity': 0.30,    # Higher (strength)
                    'recency': 0.15,     # Same
                    'cross_platform': 0.05  # Lower
                }
            elif platform == 'youtube':
                # Balanced approach
                weights = {
                    'volume': 0.30,
                    'engagement': 0.25,
                    'velocity': 0.20,
                    'recency': 0.15,
                    'cross_platform': 0.10
                }
            elif platform == 'tiktok':
                # Emphasize engagement
                weights = {
                    'volume': 0.25,      # Lower
                    'engagement': 0.30,  # Higher (strength)
                    'velocity': 0.20,
                    'recency': 0.15,
                    'cross_platform': 0.10
                }
            else:
                # Default weights
                weights = {
                    'volume': 0.30,
                    'engagement': 0.25,
                    'velocity': 0.20,
                    'recency': 0.15,
                    'cross_platform': 0.10
                }
            
            # Calculate weighted score
            trend['trending_score'] = (
                weights['volume'] * trend['volume_score'] +
                weights['engagement'] * trend['engagement_score'] +
                weights['velocity'] * trend['velocity_score'] +
                weights['recency'] * trend['recency_score'] +
                weights['cross_platform'] * trend['cross_platform_score']
            )
            
            # Round to 2 decimal places
            trend['trending_score'] = round(trend['trending_score'], 2)
            
            # Add score breakdown for transparency
            trend['score_breakdown'] = {
                'volume': round(trend['volume_score'], 2),
                'engagement': round(trend['engagement_score'], 2),
                'velocity': round(trend['velocity_score'], 2),
                'recency': round(trend['recency_score'], 2),
                'cross_platform': round(trend['cross_platform_score'], 2)
            }
            
            # Add platform-specific weights used
            trend['weights_used'] = weights
        
        # Sort by trending score (descending)
        all_trends.sort(key=lambda x: x['trending_score'], reverse=True)
        
        return all_trends

    def _calculate_volume_score(self, trend: Dict[str, Any]) -> float:
        """
        Calculate volume score based on raw reach metrics.
        
        Platform-specific metrics:
        - Google Trends: search_volume (boosted by 100x to compensate for scale)
        - YouTube: viewCount
        - TikTok: viewCount (for hashtags), followerCount (for creators)
        
        Returns raw score (will be normalized later)
        """
        platform = trend.get('platform', '')
        
        if platform == 'google_trends':
            # Google Trends search volumes are typically 1K-500K
            # YouTube/TikTok views are 100K-10M
            # Multiply by 100 to bring to similar scale
            search_volume = float(trend.get('search_volume', 0))
            return search_volume * 100  # BOOST FACTOR
        
        elif platform == 'youtube':
            return float(trend.get('viewCount', 0))
        
        elif platform == 'tiktok':
            entity_type = trend.get('entity_type', '')
            if entity_type == 'hashtag':
                return float(trend.get('viewCount', 0))
            elif entity_type == 'creator':
                # Followers are more stable than views
                return float(trend.get('followerCount', 0)) * 10  # Weight up slightly
            elif entity_type == 'sound':
                return float(trend.get('viewCount', 0))  # Approximate from related data
            elif entity_type == 'video':
                return float(trend.get('viewCount', 0))
        
        return 0.0
    
    def _calculate_engagement_score(self, trend: Dict[str, Any]) -> float:
        """
        Calculate engagement score based on interaction quality.
        
        Higher engagement rate = more genuine interest.
        Considers likes, comments, shares relative to views.
        
        Returns raw score (will be normalized later with dynamic scaling)
        """
        platform = trend.get('platform', '')
        
        if platform == 'google_trends':
            # For Google Trends, use increase_percentage as proxy for engagement
            # Return raw value - will be scaled dynamically later
            increase_pct = trend.get('increase_percentage', 0)
            return float(increase_pct)  # Return raw value
        
        elif platform == 'youtube':
            views = trend.get('viewCount', 0)
            if views == 0:
                return 0.0
            
            likes = trend.get('likeCount', 0)
            comments = trend.get('commentCount', 0)
            
            # Engagement rate formula: (likes + comments) / views * 100
            engagement_rate = ((likes + comments) / views) * 100
            
            # Scale it up for better distribution (typical ER is 2-5%)
            return engagement_rate * 1000
        
        elif platform == 'tiktok':
            entity_type = trend.get('entity_type', '')
            
            if entity_type == 'hashtag':
                video_count = trend.get('videoCount', 0)
                view_count = trend.get('viewCount', 1)  # Avoid division by zero
                # More videos per view indicates active participation
                return float(video_count) / float(view_count) * 1000000
            
            elif entity_type == 'creator':
                liked_count = trend.get('likedCount', 0)
                follower_count = trend.get('followerCount', 1)
                # Likes per follower ratio
                return (liked_count / follower_count) * 100
            
            elif entity_type == 'sound' or entity_type == 'video':
                # Use rank as proxy (lower rank = better engagement)
                rank = trend.get('rank', 100)
                return (100 - rank) * 10  # Invert so lower rank = higher score
        
        return 0.0
    
    def _normalize_engagement_scores(self, trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize Google Trends engagement scores to match YouTube/TikTok scale.
        Uses dynamic range matching based on actual engagement values from other platforms.
        
        This ensures Google Trends engagement scores are comparable with other platforms
        without causing drastic differences in the final scoring.
        """
        # Separate trends by platform
        google_trends = [t for t in trends if t.get('platform') == 'google_trends']
        other_trends = [t for t in trends if t.get('platform') != 'google_trends']
        
        if not other_trends or not google_trends:
            return trends  # Nothing to normalize
        
        # Get engagement score ranges from YouTube/TikTok
        other_scores = [t.get('engagement_score', 0) for t in other_trends if t.get('engagement_score', 0) > 0]
        
        if not other_scores:
            return trends
        
        other_min = min(other_scores)
        other_max = max(other_scores)
        other_range = other_max - other_min
        
        # Get Google Trends range
        google_scores = [t.get('engagement_score', 0) for t in google_trends]
        google_min = min(google_scores) if google_scores else 0
        google_max = max(google_scores) if google_scores else 1
        google_range = google_max - google_min if google_max != google_min else 1
        
        # Scale Google Trends to match other platforms' range
        for trend in google_trends:
            raw_score = trend.get('engagement_score', 0)
            
            # Normalize to 0-1, then scale to other platforms' range
            normalized = (raw_score - google_min) / google_range
            scaled_score = other_min + (normalized * other_range)
            
            trend['engagement_score'] = scaled_score
        
        return trends
    
    def _calculate_velocity_score(self, trend: Dict[str, Any]) -> float:
        """
        Calculate velocity score based on growth speed.
        
        Fast growth indicates viral potential and emerging trends.
        Uses trending histogram or increase percentage.
        
        Returns raw score (will be normalized later)
        """
        platform = trend.get('platform', '')
        
        if platform == 'google_trends':
            # Use a combination of increase_percentage and active status
            increase_pct = float(trend.get('increase_percentage', 0))
            
            # If trend is currently active, boost velocity
            is_active = trend.get('active', True)
            active_multiplier = 1.5 if is_active else 1.0
            
            # Calculate velocity based on increase % and activity
            # Multiply by 30 and apply active multiplier
            velocity = increase_pct * 30 * active_multiplier  # BOOST FACTOR
            
            # Bonus for very high increase percentages (1000%+)
            if increase_pct >= 1000:
                velocity *= 1.2  # Extra 20% boost for viral trends
            
            return velocity
        
        elif platform == 'youtube':
            # For YouTube, calculate velocity from views/publish time
            views = trend.get('viewCount', 0)
            published_at = trend.get('publishedAt', '')
            
            if published_at:
                try:
                    pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    hours_since_publish = max(1, (self.current_time - pub_time).total_seconds() / 3600)
                    
                    # Views per hour
                    velocity = views / hours_since_publish
                    return velocity
                except:
                    pass
            
            return float(views) / 24  # Assume 24 hours if no timestamp
        
        elif platform == 'tiktok':
            # Use trending histogram to calculate growth rate
            histogram = trend.get('trendingHistogram', [])
            
            if len(histogram) >= 2:
                # Calculate slope from first to last point
                first_val = histogram[0].get('value', 0)
                last_val = histogram[-1].get('value', 0)
                
                growth_rate = last_val - first_val
                return max(0, growth_rate) * 100  # Scale up
            
            # Fallback: use rank (lower = faster growing)
            rank = trend.get('rank', 100)
            return (100 - rank) * 10
        
        return 0.0
    
    def _calculate_recency_score(self, trend: Dict[str, Any]) -> float:
        """
        Calculate recency score using exponential decay.
        
        Formula: score = 100 * (0.5)^(age_hours / half_life)
        
        This ensures:
        - Content from 1 hour ago: ~97 score
        - Content from 24 hours ago: 50 score
        - Content from 48 hours ago: 25 score
        - Content from 1 week ago: ~1.5 score
        
        Returns score from 0-100 (already normalized)
        """
        platform = trend.get('platform', '')
        timestamp = None
        
        if platform == 'google_trends':
            timestamp = trend.get('start_timestamp')
        elif platform == 'youtube':
            published_at = trend.get('publishedAt', '')
            if published_at:
                try:
                    timestamp = datetime.fromisoformat(published_at.replace('Z', '+00:00')).timestamp()
                except:
                    pass
        elif platform == 'tiktok':
            # TikTok doesn't always provide timestamps, use trending start
            histogram = trend.get('trendingHistogram', [])
            if histogram:
                try:
                    date_str = histogram[-1].get('date', '')
                    timestamp = datetime.fromisoformat(date_str.replace('Z', '+00:00')).timestamp()
                except:
                    pass
        
        if not timestamp:
            # No timestamp available, assume recent (12 hours ago)
            return 70.0
        
        # Calculate age in hours
        age_seconds = self.current_time.timestamp() - timestamp
        age_hours = max(0, age_seconds / 3600)
        
        # Exponential decay formula
        decay_factor = age_hours / self.RECENCY_HALF_LIFE_HOURS
        recency_score = 100 * math.pow(0.5, decay_factor)
        
        return max(0, min(100, recency_score))  # Clamp to 0-100
    
    def _calculate_cross_platform_score(
        self,
        trend: Dict[str, Any],
        all_trends: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate cross-platform presence score.
        
        Items appearing on multiple platforms get bonus points.
        Uses fuzzy matching on titles/names.
        
        Returns score from 0-100 (already normalized)
        """
        # Extract key terms from this trend
        trend_terms = self._extract_key_terms(trend)
        
        if not trend_terms:
            return 0.0
        
        # Count matches across platforms
        platforms_found = set([trend.get('platform')])
        
        for other in all_trends:
            if other is trend:
                continue
            
            other_platform = other.get('platform')
            if other_platform in platforms_found:
                continue
            
            other_terms = self._extract_key_terms(other)
            
            # Check for overlap
            if self._terms_overlap(trend_terms, other_terms):
                platforms_found.add(other_platform)
        
        # Score: 0 for 1 platform, 50 for 2 platforms, 100 for 3 platforms
        num_platforms = len(platforms_found)
        
        if num_platforms == 1:
            return 0.0
        elif num_platforms == 2:
            return 50.0
        else:  # 3 or more
            return 100.0
    
    def _extract_key_terms(self, trend: Dict[str, Any]) -> set:
        """Extract searchable terms from trend item."""
        terms = set()
        
        # Get title/name/query
        text = (
            trend.get('query', '') or
            trend.get('title', '') or
            trend.get('name', '') or
            ''
        )
        
        # Normalize and split
        text = text.lower()
        words = text.split()
        
        # Remove common stop words and keep significant terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'vs', 'x'}
        significant_words = [w for w in words if len(w) > 2 and w not in stop_words]
        
        terms.update(significant_words)
        
        return terms
    
    def _terms_overlap(self, terms1: set, terms2: set, threshold: float = 0.3) -> bool:
        """
        Check if two term sets overlap significantly.
        
        Args:
            terms1: First set of terms
            terms2: Second set of terms
            threshold: Minimum overlap ratio (default: 30%)
            
        Returns:
            True if overlap exceeds threshold
        """
        if not terms1 or not terms2:
            return False
        
        intersection = terms1.intersection(terms2)
        union = terms1.union(terms2)
        
        if not union:
            return False
        
        overlap_ratio = len(intersection) / len(union)
        return overlap_ratio >= threshold
    
    def _normalize_scores(self, trends: List[Dict[str, Any]], score_key: str):
        """
        Normalize a score to 0-100 scale using min-max normalization.
        
        Args:
            trends: List of trend items
            score_key: Key of the score to normalize
        """
        if not trends:
            return
        
        scores = [t.get(score_key, 0) for t in trends]
        min_score = min(scores)
        max_score = max(scores)
        
        # Handle case where all scores are the same
        if max_score == min_score:
            for trend in trends:
                trend[score_key] = 50.0  # Set to middle value
            return
        
        # Min-max normalization to 0-100
        for trend in trends:
            raw_score = trend.get(score_key, 0)
            normalized = ((raw_score - min_score) / (max_score - min_score)) * 100
            trend[score_key] = normalized