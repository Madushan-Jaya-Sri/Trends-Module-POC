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
        # Max values for TikTok normalization
        self.max_hashtag_views = 1
        self.max_hashtag_videos = 1
        self.max_hashtag_rank = 1
        self.max_sound_rank = 1
        self.max_video_rank = 1
        
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

        # Count trends by platform
        platform_counts = {}
        for trend in all_trends:
            platform = trend.get('platform', 'unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1

        logger.info(f"[SCORING START] Processing {len(all_trends)} trends: {platform_counts}")

        # Pre-calculate max values for TikTok normalization
        self._calculate_tiktok_max_values(all_trends)

        # Calculate individual component scores
        logger.info(f"[SCORING] Calculating raw component scores (volume, engagement, velocity, recency, cross-platform)...")
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
        logger.info(f"[FINAL SCORE] Calculating final weighted scores for {len(all_trends)} trends")

        for trend in all_trends:
            platform = trend.get('platform', '')
            trend_name = trend.get('query') or trend.get('title') or trend.get('name', 'Unknown')

            # Choose weights based on platform
            if platform == 'google_trends':
                # Emphasize what Google Trends is good at
                weights = {
                    'volume': 0.10,      # Lower
                    'engagement': 0.15,  # Lower (limited data)
                    'velocity': 0.30,    # Higher (strength)
                    'recency': 0.35,     # Higher (to compensate)
                    'cross_platform': 0.10  # Lower
                }
            elif platform == 'youtube':
                # Balanced approach
                weights = {
                    'volume': 0.10,
                    'engagement': 0.35,
                    'velocity': 0.25,
                    'recency': 0.20,
                    'cross_platform': 0.10
                }
            elif platform == 'tiktok':
                # TikTok: Use entity-type-specific weights
                entity_type = trend.get('entity_type', '')

                if entity_type == 'hashtag':
                    # Hashtags: Emphasize engagement (viewCount, videoCount, rank, momentum)
                    weights = {
                        'volume': 0.15,
                        'engagement': 0.35,  # Strongest - rich engagement metrics
                        'velocity': 0.25,
                        'recency': 0.20,
                        'cross_platform': 0.05
                    }
                elif entity_type == 'creator':
                    # Creators: Emphasize velocity (enhanced with relatedVideos data)
                    weights = {
                        'volume': 0.10,
                        'engagement': 0.30,
                        'velocity': 0.30,    # Strongest - views/day, likes/day, posting frequency
                        'recency': 0.20,
                        'cross_platform': 0.10
                    }
                elif entity_type == 'sound':
                    # Sounds: Balanced with emphasis on engagement and velocity
                    weights = {
                        'volume': 0.01,
                        'engagement': 0.30,
                        'velocity': 0.30,
                        'recency': 0.24,
                        'cross_platform': 0.15
                    }
                elif entity_type == 'video':
                    # Videos: Balanced with emphasis on engagement and velocity
                    weights = {
                        'volume': 0.01,
                        'engagement': 0.80,
                        'velocity': 0.01,
                        'recency': 0.01,
                        'cross_platform': 0.17
                    }
                else:
                    # Default TikTok weights (if entity_type is missing)
                    weights = {
                        'volume': 0.25,
                        'engagement': 0.30,
                        'velocity': 0.20,
                        'recency': 0.15,
                        'cross_platform': 0.10
                    }
            else:
                # Default weights
                weights = {
                    'volume': 0.25,
                    'engagement': 0.30,
                    'velocity': 0.20,
                    'recency': 0.15,
                    'cross_platform': 0.10
                }

            # Calculate weighted score
            vol_contribution = weights['volume'] * trend['volume_score']
            eng_contribution = weights['engagement'] * trend['engagement_score']
            vel_contribution = weights['velocity'] * trend['velocity_score']
            rec_contribution = weights['recency'] * trend['recency_score']
            cross_contribution = weights['cross_platform'] * trend['cross_platform_score']

            trend['trending_score'] = (
                vol_contribution +
                eng_contribution +
                vel_contribution +
                rec_contribution +
                cross_contribution
            )

            # Round to 2 decimal places
            trend['trending_score'] = round(trend['trending_score'], 2)

            # Log the calculation details
            platform_label = f"{platform.replace('_', ' ').title()}"
            if platform == 'tiktok':
                entity_type = trend.get('entity_type', '')
                platform_label += f" {entity_type.capitalize()}"

            logger.debug(
                f"[FINAL SCORE] {platform_label} '{trend_name}': "
                f"vol={trend['volume_score']:.2f}×{weights['volume']:.2f}={vol_contribution:.2f}, "
                f"eng={trend['engagement_score']:.2f}×{weights['engagement']:.2f}={eng_contribution:.2f}, "
                f"vel={trend['velocity_score']:.2f}×{weights['velocity']:.2f}={vel_contribution:.2f}, "
                f"rec={trend['recency_score']:.2f}×{weights['recency']:.2f}={rec_contribution:.2f}, "
                f"cross={trend['cross_platform_score']:.2f}×{weights['cross_platform']:.2f}={cross_contribution:.2f} "
                f"→ TRENDING_SCORE={trend['trending_score']:.2f}"
            )

            # Add score breakdown showing percentage of total (0-100 scale)
            # These scores represent the proportion of the total for each metric
            # All volumes sum to 100%, all engagements sum to 100%, etc.
            # Example: volume=25% means this trend represents 25% of total volume
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

        # Log summary of top trends
        logger.info(f"[SCORING COMPLETE] Sorted {len(all_trends)} trends by trending_score")
        if all_trends:
            top_5 = all_trends[:min(5, len(all_trends))]
            logger.info(f"[TOP TRENDS] Top {len(top_5)} trends:")
            for i, trend in enumerate(top_5, 1):
                trend_name = trend.get('query') or trend.get('title') or trend.get('name', 'Unknown')
                platform = trend.get('platform', 'unknown').replace('_', ' ').title()
                if trend.get('platform') == 'tiktok':
                    platform += f" {trend.get('entity_type', '').capitalize()}"
                logger.info(
                    f"  #{i} [{platform}] '{trend_name}' - Score: {trend['trending_score']:.2f} "
                    f"(vol={trend['volume_score']:.1f}, eng={trend['engagement_score']:.1f}, "
                    f"vel={trend['velocity_score']:.1f}, rec={trend['recency_score']:.1f})"
                )

        return all_trends

    def _calculate_tiktok_max_values(self, all_trends: List[Dict[str, Any]]):
        """
        Pre-calculate maximum values for all TikTok entity types for relative normalization.

        Args:
            all_trends: List of all trending items
        """
        # Filter TikTok items by entity type
        tiktok_hashtags = [
            t for t in all_trends
            if t.get('platform') == 'tiktok' and t.get('entity_type') == 'hashtag'
        ]
        tiktok_sounds = [
            t for t in all_trends
            if t.get('platform') == 'tiktok' and t.get('entity_type') == 'sound'
        ]
        tiktok_videos = [
            t for t in all_trends
            if t.get('platform') == 'tiktok' and t.get('entity_type') == 'video'
        ]

        # Find max values for hashtags
        if tiktok_hashtags:
            self.max_hashtag_views = max(
                (float(h.get('viewCount', 0)) for h in tiktok_hashtags),
                default=1
            )
            self.max_hashtag_videos = max(
                (float(h.get('videoCount', 0)) for h in tiktok_hashtags),
                default=1
            )
            self.max_hashtag_rank = max(
                (float(h.get('rank', 1)) for h in tiktok_hashtags),
                default=1
            )

        # Find max rank for sounds
        if tiktok_sounds:
            self.max_sound_rank = max(
                (float(s.get('rank', 1)) for s in tiktok_sounds),
                default=1
            )

        # Find max rank for videos
        if tiktok_videos:
            self.max_video_rank = max(
                (float(v.get('rank', 1)) for v in tiktok_videos),
                default=1
            )

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
        trend_name = trend.get('query') or trend.get('title') or trend.get('name', 'Unknown')

        if platform == 'google_trends':
            # Google Trends search volumes are typically 1K-500K
            # YouTube/TikTok views are 100K-10M
            # Multiply by 100 to bring to similar scale
            search_volume = float(trend.get('search_volume', 0))
            volume_score = search_volume * 100  # BOOST FACTOR
            logger.debug(f"[VOLUME] Google Trends '{trend_name}': search_volume={search_volume:,.0f} → score={volume_score:,.2f} (boosted 100x)")
            return volume_score

        elif platform == 'youtube':
            view_count = float(trend.get('viewCount', 0))
            logger.debug(f"[VOLUME] YouTube '{trend_name}': viewCount={view_count:,.0f} → score={view_count:,.2f}")
            return view_count

        elif platform == 'tiktok':
            entity_type = trend.get('entity_type', '')
            if entity_type == 'hashtag':
                view_count = float(trend.get('viewCount', 0))
                logger.debug(f"[VOLUME] TikTok Hashtag '{trend_name}': viewCount={view_count:,.0f} → score={view_count:,.2f}")
                return view_count
            elif entity_type == 'creator':
                # Followers are more stable than views
                follower_count = float(trend.get('followerCount', 0))
                volume_score = follower_count * 10  # Weight up slightly
                logger.debug(f"[VOLUME] TikTok Creator '{trend_name}': followerCount={follower_count:,.0f} → score={volume_score:,.2f} (weighted 10x)")
                return volume_score
            elif entity_type == 'sound':
                rank = float(trend.get('rank', 0))
                logger.debug(f"[VOLUME] TikTok Sound '{trend_name}': rank={rank} → score={rank:.2f}")
                return rank
            elif entity_type == 'video':
                rank = float(trend.get('rank', 0))
                logger.debug(f"[VOLUME] TikTok Video '{trend_name}': rank={rank} → score={rank:.2f}")
                return rank

        logger.debug(f"[VOLUME] Unknown platform '{platform}' for '{trend_name}' → score=0.0")
        return 0.0
    
    def _calculate_engagement_score(self, trend: Dict[str, Any]) -> float:
        """
        Calculate engagement score based on interaction quality.

        Higher engagement rate = more genuine interest.
        Considers likes, comments, shares relative to views.

        Returns raw score (will be normalized later with dynamic scaling)
        """
        platform = trend.get('platform', '')
        trend_name = trend.get('query') or trend.get('title') or trend.get('name', 'Unknown')

        if platform == 'google_trends':
            # For Google Trends, use increase_percentage as proxy for engagement
            # Return raw value - will be scaled dynamically later
            increase_pct = trend.get('increase_percentage', 0)
            logger.debug(f"[ENGAGEMENT] Google Trends '{trend_name}': increase_pct={increase_pct}% → score={increase_pct:.2f}")
            return float(increase_pct)  # Return raw value

        elif platform == 'youtube':
            views = trend.get('viewCount', 0)
            if views == 0:
                logger.debug(f"[ENGAGEMENT] YouTube '{trend_name}': viewCount=0 → score=0.0 (no views)")
                return 0.0

            likes = trend.get('likeCount', 0)
            comments = trend.get('commentCount', 0)

            # Engagement rate formula: (likes + comments) / views
            # This ensures videos with the same likes+comments but different views get different scores
            engagement_rate = (likes + comments) / views

            # Scale by 1M to get reasonable numbers for normalization
            # Typical engagement rates are 2-5%, so 0.02-0.05
            # Multiply by 1M to get 20,000-50,000 range
            engagement_score = engagement_rate * 1_000_000

            logger.debug(
                f"[ENGAGEMENT] YouTube '{trend_name}': views={views:,.0f}, likes={likes:,.0f}, comments={comments:,.0f} "
                f"→ rate={engagement_rate:.4f} ({engagement_rate*100:.2f}%) → score={engagement_score:,.2f}"
            )
            return engagement_score
        
        elif platform == 'tiktok':
            entity_type = trend.get('entity_type', '')

            if entity_type == 'hashtag':
                # Enhanced engagement calculation for hashtags with relative normalization
                view_count = float(trend.get('viewCount', 0))
                video_count = float(trend.get('videoCount', 0))
                rank = float(trend.get('rank', 100))

                # Relative logarithmic normalization for views and videos
                # view_norm = log(viewCount + 1) / log(max_viewCount + 1)
                # view_norm = math.log(view_count + 1) / math.log(self.max_hashtag_views + 1)
                view_norm = (view_count)/ (self.max_hashtag_views)

                # video_norm = log(videoCount + 1) / log(max_videoCount + 1)
                # video_norm = math.log(video_count + 1) / math.log(self.max_hashtag_videos + 1)
                video_norm = (video_count) / (self.max_hashtag_videos)
                # Rank normalization (lower rank = better, so invert)
                # rank_norm = 1 - (rank / max_rank)
                rank_norm = 1 - (rank / self.max_hashtag_rank)

                # Momentum from trending histogram (slope calculation)
                momentum_norm = self._calculate_histogram_momentum(trend)

                # Weighted engagement score
                engagement_score = (
                    (0.45 * view_norm) +
                    (0.30 * video_norm) +
                    (0.15 * rank_norm) +
                    (0.10 * momentum_norm)
                )

                logger.debug(
                    f"[ENGAGEMENT] TikTok Hashtag '{trend_name}': views={view_count:,.0f} (norm={view_norm:.4f}), "
                    f"videos={video_count:,.0f} (norm={video_norm:.4f}), rank={rank} (norm={rank_norm:.4f}), "
                    f"momentum={momentum_norm:.4f} → score={engagement_score:.4f}"
                )
                return engagement_score

            elif entity_type == 'creator':
                liked_count = trend.get('likedCount', 0)
                follower_count = trend.get('followerCount', 1)
                # Likes per follower ratio
                engagement_score = (liked_count / follower_count) * 100
                logger.debug(
                    f"[ENGAGEMENT] TikTok Creator '{trend_name}': likes={liked_count:,.0f}, followers={follower_count:,.0f} "
                    f"→ ratio={liked_count/follower_count:.4f} → score={engagement_score:.2f}"
                )
                return engagement_score

            elif entity_type == 'sound':
                # Use rank normalization (lower rank = better engagement)
                rank = float(trend.get('rank', self.max_sound_rank))
                # rank_norm = 1 - (rank / max_rank)
                rank_norm = 1 - (rank / self.max_sound_rank)
                engagement_score = rank_norm * 100  # Scale to 0-100
                logger.debug(f"[ENGAGEMENT] TikTok Sound '{trend_name}': rank={rank} (norm={rank_norm:.4f}) → score={engagement_score:.2f}")
                return engagement_score

            elif entity_type == 'video':
                # Use rank normalization (lower rank = better engagement)
                rank = float(trend.get('rank', self.max_video_rank))
                # rank_norm = 1 - (rank / max_rank)
                rank_norm = 1 - (rank / self.max_video_rank)
                engagement_score = rank_norm * 100  # Scale to 0-100
                logger.debug(f"[ENGAGEMENT] TikTok Video '{trend_name}': rank={rank} (norm={rank_norm:.4f}) → score={engagement_score:.2f}")
                return engagement_score

        logger.debug(f"[ENGAGEMENT] Unknown platform '{platform}' for '{trend_name}' → score=0.0")
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
        trend_name = trend.get('query') or trend.get('title') or trend.get('name', 'Unknown')

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
            viral_bonus = ""
            if increase_pct >= 1000:
                velocity *= 1.2  # Extra 20% boost for viral trends
                viral_bonus = " +20% viral bonus"

            logger.debug(
                f"[VELOCITY] Google Trends '{trend_name}': increase_pct={increase_pct}%, active={is_active} "
                f"(multiplier={active_multiplier}x) → score={velocity:,.2f}{viral_bonus}"
            )
            return velocity

        elif platform == 'youtube':
            # For YouTube, calculate velocity from views/publish time
            views = trend.get('viewCount', 0)
            likes = trend.get('likeCount', 0)
            comments = trend.get('commentCount', 0)
            published_at = trend.get('publishedAt', '')

            if published_at:
                try:
                    pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    hours_since_publish = max(1, (self.current_time - pub_time).total_seconds() / 3600)

                    # Combined velocity: views per hour + engagement per hour
                    # Weight views more heavily (70%) than engagement (30%)
                    view_velocity = views / hours_since_publish
                    engagement_velocity = (likes + comments) / hours_since_publish

                    # Combined velocity with weighted average
                    velocity = (view_velocity * 0.7) + (engagement_velocity * 0.3)
                    logger.debug(
                        f"[VELOCITY] YouTube '{trend_name}': {hours_since_publish:.1f}h old, "
                        f"view_vel={view_velocity:,.1f}/h (70%), eng_vel={engagement_velocity:,.1f}/h (30%) "
                        f"→ score={velocity:,.2f}"
                    )
                    return velocity
                except:
                    pass

            # Fallback: assume 24 hours if no timestamp
            view_velocity = float(views) / 24
            engagement_velocity = float(likes + comments) / 24
            velocity = (view_velocity * 0.7) + (engagement_velocity * 0.3)
            logger.debug(f"[VELOCITY] YouTube '{trend_name}': no timestamp, assuming 24h → score={velocity:,.2f}")
            return velocity
        
        elif platform == 'tiktok':
            entity_type = trend.get('entity_type', '')

            # Special handling for creators - use relatedVideos data
            if entity_type == 'creator':
                related_videos = trend.get('relatedVideos', [])

                if related_videos and len(related_videos) >= 2:
                    # Extract data from related videos
                    total_views = 0
                    total_likes = 0
                    video_times = []

                    for video in related_videos:
                        total_views += video.get('viewCount', 0)
                        total_likes += video.get('likedCount', 0)

                        create_time = video.get('createTime')
                        if create_time:
                            try:
                                video_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                                video_times.append(video_time)
                            except:
                                pass

                    # Calculate time span and velocity metrics
                    if len(video_times) >= 2:
                        video_times.sort()
                        oldest_video = video_times[0]
                        newest_video = video_times[-1]

                        # Calculate days between oldest and newest video
                        time_span = (newest_video - oldest_video).total_seconds() / 86400  # Convert to days
                        time_span = max(1, time_span)  # Avoid division by zero

                        # Calculate metrics
                        views_per_day = total_views / time_span
                        likes_per_day = total_likes / time_span
                        posting_frequency = len(related_videos) / time_span  # Videos per day

                        # Composite velocity score
                        # Weight: 50% views/day, 30% likes/day, 20% posting frequency
                        velocity = (
                            (0.50 * views_per_day) +
                            (0.30 * likes_per_day) +
                            (0.20 * posting_frequency * 100000)  # Scale up posting frequency
                        )

                        logger.debug(
                            f"[VELOCITY] TikTok Creator '{trend_name}': {len(related_videos)} videos over {time_span:.1f} days, "
                            f"views/day={views_per_day:,.1f} (50%), likes/day={likes_per_day:,.1f} (30%), "
                            f"posting_freq={posting_frequency:.2f}/day (20%) → score={velocity:,.2f}"
                        )
                        return velocity

            # For hashtags, sounds, videos - use trending histogram
            histogram = trend.get('trendingHistogram', [])

            if len(histogram) >= 2:
                # Calculate slope from first to last point
                first_val = histogram[0].get('value', 0)
                last_val = histogram[-1].get('value', 0)

                growth_rate = last_val - first_val
                velocity = max(0, growth_rate) * 100  # Scale up
                logger.debug(
                    f"[VELOCITY] TikTok {entity_type.capitalize()} '{trend_name}': histogram growth={first_val}→{last_val} "
                    f"(rate={growth_rate}) → score={velocity:,.2f}"
                )
                return velocity

            # Fallback: use rank (lower = faster growing)
            rank = trend.get('rank', 100)
            velocity = (100 - rank) * 10
            logger.debug(f"[VELOCITY] TikTok {entity_type.capitalize()} '{trend_name}': rank={rank} → score={velocity:.2f} (fallback)")
            return velocity

        logger.debug(f"[VELOCITY] Unknown platform '{platform}' for '{trend_name}' → score=0.0")
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
        trend_name = trend.get('query') or trend.get('title') or trend.get('name', 'Unknown')
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
            entity_type = trend.get('entity_type', '')

            # Special handling for creators - use most recent video's createTime
            if entity_type == 'creator':
                related_videos = trend.get('relatedVideos', [])
                if related_videos:
                    # Find the most recent video
                    most_recent_time = None
                    for video in related_videos:
                        create_time = video.get('createTime')
                        if create_time:
                            try:
                                video_time = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                                if most_recent_time is None or video_time > most_recent_time:
                                    most_recent_time = video_time
                            except:
                                pass

                    if most_recent_time:
                        timestamp = most_recent_time.timestamp()

            # For other TikTok items (hashtags, sounds, videos) - use trending histogram
            if not timestamp:
                histogram = trend.get('trendingHistogram', [])
                if histogram:
                    try:
                        date_str = histogram[-1].get('date', '')
                        timestamp = datetime.fromisoformat(date_str.replace('Z', '+00:00')).timestamp()
                    except:
                        pass

        if not timestamp:
            # No timestamp available, assume recent (12 hours ago)
            logger.debug(f"[RECENCY] {platform.replace('_', ' ').title()} '{trend_name}': no timestamp → score=70.0 (default)")
            return 70.0

        # Calculate age in hours
        age_seconds = self.current_time.timestamp() - timestamp
        age_hours = max(0, age_seconds / 3600)

        # Exponential decay formula
        decay_factor = age_hours / self.RECENCY_HALF_LIFE_HOURS
        recency_score = 100 * math.pow(0.5, decay_factor)

        # Format age for display
        if age_hours < 1:
            age_str = f"{age_hours*60:.0f}m"
        elif age_hours < 24:
            age_str = f"{age_hours:.1f}h"
        else:
            age_str = f"{age_hours/24:.1f}d"

        logger.debug(
            f"[RECENCY] {platform.replace('_', ' ').title()} '{trend_name}': age={age_str} "
            f"(decay_factor={decay_factor:.2f}) → score={recency_score:.2f}"
        )

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
    
    def _calculate_histogram_momentum(self, trend: Dict[str, Any]) -> float:
        """
        Calculate momentum (trending speed) from trending histogram using slope.

        Args:
            trend: Trend item with trendingHistogram data

        Returns:
            Momentum score based on slope of trending data
        """
        histogram = trend.get('trendingHistogram', [])

        if not histogram or len(histogram) < 2:
            return 0.0

        # Extract values from histogram
        values = [point.get('value', 0) for point in histogram]

        # Calculate simple linear regression slope
        n = len(values)
        x_values = list(range(n))  # Time points: 0, 1, 2, ...

        # Calculate means
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n

        # Calculate slope using least squares method
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Return absolute slope scaled up (can be positive or negative)
        # Scale by 100 to bring to similar magnitude as other components
        return abs(slope) * 100

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
        Normalize scores to percentage of total (0-100 scale).

        Each score represents the proportion of the total for that metric.
        All scores for a metric sum to 100%.

        Example:
        - Trend A: volume 1000, Trend B: volume 500, Trend C: volume 500
        - Total: 2000
        - A: (1000/2000)*100 = 50%, B: 25%, C: 25%
        - Sum: 50 + 25 + 25 = 100%

        Args:
            trends: List of trend items
            score_key: Key of the score to normalize
        """
        if not trends:
            return

        scores = [t.get(score_key, 0) for t in trends]
        total_score = sum(scores)
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 0
        avg_score = total_score / len(scores) if scores else 0

        logger.info(f"[NORMALIZE] {score_key}: {len(trends)} trends")
        logger.info(f"[NORMALIZE] {score_key} RAW VALUES: min={min_score:.2f}, max={max_score:.2f}, avg={avg_score:.2f}, total={total_score:.2f}")

        # Handle case where all scores are zero
        if total_score == 0:
            logger.info(f"[NORMALIZE] All {score_key} values are zero, setting all to equal distribution")
            equal_percentage = 100.0 / len(trends)
            for trend in trends:
                trend[score_key] = equal_percentage
            logger.info(f"[NORMALIZE] {score_key} RESULT: Each trend = {equal_percentage:.2f}%")
            return

        # Calculate percentage of total
        normalized_values = []
        for trend in trends:
            raw_score = trend.get(score_key, 0)
            percentage = (raw_score / total_score) * 100
            trend[score_key] = percentage
            normalized_values.append(percentage)

        # Verify sum equals 100 (allowing for small floating point errors)
        total_percentage = sum(normalized_values)
        min_pct = min(normalized_values) if normalized_values else 0
        max_pct = max(normalized_values) if normalized_values else 0
        avg_pct = total_percentage / len(normalized_values) if normalized_values else 0

        # Count how many trends have very high or very low percentages
        count_high = sum(1 for v in normalized_values if v > 10.0)
        count_low = sum(1 for v in normalized_values if v < 0.1)

        logger.info(f"[NORMALIZE] {score_key} PERCENTAGES: min={min_pct:.2f}%, max={max_pct:.2f}%, avg={avg_pct:.2f}%, total={total_percentage:.2f}%")
        logger.info(f"[NORMALIZE] {score_key} DISTRIBUTION: >10%: {count_high} trends, <0.1%: {count_low} trends")

    def calculate_platform_specific_scores(
        self,
        trends: List[Dict[str, Any]],
        platform: str
    ) -> List[Dict[str, Any]]:
        """
        Calculate trending scores for items from a single platform.

        This uses the same scoring methodology as unified scoring but:
        - Only scores items from the specified platform
        - Cross-platform score is set to 0 (not applicable)
        - Uses platform-specific weights
        - Normalizes within the platform's dataset

        Args:
            trends: List of trend items from a single platform
            platform: Platform name ('google_trends', 'youtube', or 'tiktok')

        Returns:
            List of trends with trending_score added, sorted by score
        """
        if not trends:
            return []

        # Pre-calculate TikTok max values if needed
        if platform == 'tiktok':
            self._calculate_tiktok_max_values(trends)

        # Calculate individual component scores
        for trend in trends:
            trend['volume_score'] = self._calculate_volume_score(trend)
            trend['engagement_score'] = self._calculate_engagement_score(trend)
            trend['velocity_score'] = self._calculate_velocity_score(trend)
            trend['recency_score'] = self._calculate_recency_score(trend)
            trend['cross_platform_score'] = 0.0  # Not applicable for single platform

        # Normalize component scores to 0-100 scale
        self._normalize_scores(trends, 'volume_score')
        self._normalize_scores(trends, 'engagement_score')
        self._normalize_scores(trends, 'velocity_score')
        # recency_score is already normalized (0-100)

        # Calculate final weighted score with entity-type-specific weights for TikTok
        for trend in trends:
            # Get platform-specific weights
            if platform == 'google_trends':
                weights = {
                    'volume': 0.10,      # Increased (no cross-platform)
                    'engagement': 0.15,  # Lower (limited data)
                    'velocity': 0.35,    # Higher (strength)
                    'recency': 0.40,     # Same
                    'cross_platform': 0.0
                }
            elif platform == 'youtube':
                weights = {
                    'volume': 0.35,
                    'engagement': 0.30,
                    'velocity': 0.20,
                    'recency': 0.15,
                    'cross_platform': 0.0
                }
            elif platform == 'tiktok':
                # Use entity-type-specific weights for TikTok
                entity_type = trend.get('entity_type', '')

                if entity_type == 'hashtag':
                    # Hashtags: Emphasize engagement (viewCount, videoCount, rank, momentum)
                    weights = {
                        'volume': 0.20,
                        'engagement': 0.35,  # Strongest - rich engagement metrics
                        'velocity': 0.25,
                        'recency': 0.20,
                        'cross_platform': 0.0
                    }
                elif entity_type == 'creator':
                    # Creators: Emphasize velocity (enhanced with relatedVideos data)
                    weights = {
                        'volume': 0.20,
                        'engagement': 0.30,
                        'velocity': 0.30,    # Strongest - views/day, likes/day, posting frequency
                        'recency': 0.20,
                        'cross_platform': 0.0
                    }
                elif entity_type == 'sound':
                    # Sounds: Balanced with emphasis on engagement and velocity
                    weights = {
                        'volume': 0.0,
                        'engagement': 0.35,
                        'velocity': 0.35,
                        'recency': 0.30,
                        'cross_platform': 0.0
                    }
                elif entity_type == 'video':
                    # Videos: Balanced with emphasis on engagement and velocity
                    weights = {
                        'volume': 0.0,
                        'engagement': 1.0,
                        'velocity': 0.0,
                        'recency': 0.0,
                        'cross_platform': 0.0
                    }
                else:
                    # Default TikTok weights (if entity_type is missing)
                    weights = {
                        'volume': 0.30,
                        'engagement': 0.35,
                        'velocity': 0.20,
                        'recency': 0.15,
                        'cross_platform': 0.0
                    }
            else:
                # Default weights
                weights = {
                    'volume': 0.35,
                    'engagement': 0.30,
                    'velocity': 0.20,
                    'recency': 0.15,
                    'cross_platform': 0.0
                }

            # Calculate weighted score
            trend['trending_score'] = (
                weights['volume'] * trend['volume_score'] +
                weights['engagement'] * trend['engagement_score'] +
                weights['velocity'] * trend['velocity_score'] +
                weights['recency'] * trend['recency_score']
            )

            # Round to 2 decimal places
            trend['trending_score'] = round(trend['trending_score'], 2)

            # Add score breakdown showing percentage of total (0-100 scale)
            # These scores represent the proportion of the total for each metric within the platform
            # All volumes for this platform sum to 100%, all engagements sum to 100%, etc.
            # Example: volume=25% means this trend represents 25% of total volume in this platform
            trend['score_breakdown'] = {
                'volume': round(trend['volume_score'], 2),
                'engagement': round(trend['engagement_score'], 2),
                'velocity': round(trend['velocity_score'], 2),
                'recency': round(trend['recency_score'], 2)
            }

            # Add entity-type-specific weights used (for transparency)
            trend['weights_used'] = weights

        # Sort by trending score (descending)
        trends.sort(key=lambda x: x['trending_score'], reverse=True)

        return trends