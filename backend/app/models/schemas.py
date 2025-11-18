from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from ..constants import UnifiedCategory


# ======================= GOOGLE TRENDS SCHEMAS =======================

class GoogleTrendsRequest(BaseModel):
    """Request schema for Google Trends endpoint"""
    country_code: str = Field(
        default="US",
        description="Two-letter country code (e.g., 'US', 'IN', 'LK')"
    )
    category: Optional[UnifiedCategory] = Field(
        default=None,
        description="Optional category filter for trending searches"
    )
    time_period: Optional[str] = Field(
        default=None,
        description="Time period filter: '4h' (Past 4 hours), '24h' (Past 24 hours), '48h' (Past 48 hours), '7d' (Past 7 days)"
    )


class GoogleTrendsResponse(BaseModel):
    """Response schema for Google Trends data"""
    country: str
    timestamp: str
    total_trends: int
    trending_searches: List[Dict[str, Any]]


# ======================= TIKTOK SCHEMAS =======================

class TikTokRequest(BaseModel):
    """Request schema for TikTok trends endpoint"""
    country_code: str = Field(
        default="MY",
        description="Two-letter country code (e.g., 'MY', 'US', 'IN')"
    )
    results_per_page: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of results per category"
    )
    time_range: str = Field(
        default="7",
        description="Time range in days (deprecated - use time_period instead)"
    )
    time_period: Optional[str] = Field(
        default=None,
        description="Time period filter: '7d' (Past 7 days), '30d' (Past 30 days), '120d' (Past 120 days)"
    )
    category: Optional[UnifiedCategory] = Field(
        default=None,
        description="Optional category filter for trending content"
    )


class TikTokHashtag(BaseModel):
    """Schema for TikTok hashtag"""
    name: Optional[str] = None
    countryCode: Optional[str] = None
    rank: Optional[int] = None
    trendingHistogram: List[Dict[str, Any]] = []
    url: Optional[str] = None
    videoCount: Optional[int] = None
    viewCount: Optional[int] = None
    industryName: Optional[str] = None
    relatedCreators: List[Dict[str, Any]] = []


class TikTokCreator(BaseModel):
    """Schema for TikTok creator"""
    avatar: Optional[str] = None
    countryCode: Optional[str] = None
    followerCount: Optional[int] = None
    likedCount: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None
    rank: Optional[int] = None
    relatedVideos: List[Dict[str, Any]] = []


class TikTokSound(BaseModel):
    """Schema for TikTok sound"""
    name: Optional[str] = None
    countryCode: Optional[str] = None
    rank: Optional[int] = None
    trendingHistogram: List[Dict[str, Any]] = []
    url: Optional[str] = None
    coverUrl: Optional[str] = None
    durationSec: Optional[int] = None
    author: Optional[str] = None


class TikTokVideo(BaseModel):
    """Schema for TikTok video"""
    countryCode: Optional[str] = None
    coverUrl: Optional[str] = None
    durationSec: Optional[int] = None
    rank: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None


class TikTokResponse(BaseModel):
    """Response schema for TikTok trends data"""
    country: str
    timestamp: str
    hashtags: List[Dict[str, Any]]
    creators: List[Dict[str, Any]]
    sounds: List[Dict[str, Any]]
    videos: List[Dict[str, Any]]
    total_items: Dict[str, int]


# ======================= YOUTUBE SCHEMAS =======================

class YouTubeRequest(BaseModel):
    """Request schema for YouTube trends endpoint"""
    country_code: str = Field(
        default="US",
        description="Two-letter country code (e.g., 'US', 'MY', 'IN')"
    )
    max_results: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of videos to fetch"
    )
    category: Optional[UnifiedCategory] = Field(
        default=None,
        description="Optional category filter for trending videos"
    )
    time_period: Optional[str] = Field(
        default=None,
        description="Time period filter: '1d' (Past 1 day), '7d' (Past 7 days), '30d' (Past 30 days), '90d' (Past 90 days)"
    )


class YouTubeVideo(BaseModel):
    """Schema for YouTube video with comprehensive metadata"""
    kind: str
    id: str
    publishedAt: str
    channelId: str
    channelTitle: str
    title: str
    description: str
    tags: List[str] = []
    categoryId: str
    defaultLanguage: Optional[str] = None
    liveBroadcastContent: str
    thumbnail_url_standard: str
    duration_sec: int
    dimension: str
    definition: str
    caption: bool
    licensedContent: bool
    projection: str
    viewCount: int
    likeCount: int
    favoriteCount: int
    commentCount: int
    localized_title: str
    localized_description: str
    etag: str


class YouTubeResponse(BaseModel):
    """Response schema for YouTube trends data"""
    country: str
    timestamp: str
    total_videos: int
    videos: List[Dict[str, Any]]


# ======================= UNIFIED TRENDING SCHEMAS =======================

class UnifiedTrendingRequest(BaseModel):
    """Request schema for unified trending endpoint"""
    country_code: str = Field(
        default="US",
        description="Two-letter country code (e.g., 'US', 'MY', 'IN', 'LK')"
    )
    category: Optional[UnifiedCategory] = Field(
        default=None,
        description="Optional category filter for all platforms"
    )
    max_results_per_platform: int = Field(
        default=10,
        ge=5,
        le=50,
        description="Maximum results to fetch per platform"
    )
    time_range: Optional[str] = Field(
        default="7d",
        description="Filter by time range: '24h' (Past 24 hours), '7d' (Past 7 days - default), '30d' (Past 30 days), '90d' (Past 90 days)"
    )
    limit: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Number of top trends to return (after scoring)"
    )


class TrendItem(BaseModel):
    """Schema for a unified trend item with score"""
    platform: str
    entity_type: str
    id: str
    title: str
    name: str
    url: str
    trending_score: float
    score_breakdown: Dict[str, float]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    raw_data: Optional[Dict[str, Any]] = None


class UnifiedTrendingResponse(BaseModel):
    """Response schema for unified trending data"""
    country: str
    timestamp: str
    time_range: Optional[str]
    total_trends_analyzed: int
    returned_trends: int
    platform_counts: Dict[str, int]
    score_methodology: Dict[str, Any]
    trends: List[Dict[str, Any]]


# ======================= DETAILS ENDPOINTS SCHEMAS =======================

class GoogleTrendsDetailsRequest(BaseModel):
    """Request schema for Google Trends details endpoint"""
    query: str = Field(..., description="The search query to get details for")
    country_code: str = Field(
        default="US",
        description="Two-letter country code (e.g., 'US', 'IN', 'LK')"
    )
    date: str = Field(
        default="today 12-m",
        description="Time period (e.g., 'today 12-m', 'today 3-m', 'today 1-m')"
    )
    include_region_drill_down: bool = Field(
        default=False,
        description="Include city-level data for top regions (for initial request)"
    )
    geo: Optional[str] = Field(
        default=None,
        description="Geographic code for drill-down (e.g., 'LK-1' for Western Province). Used when fetching city-level data for a specific region."
    )
    region_level: Optional[str] = Field(
        default=None,
        description="Region level: 'REGION' for provinces/states, 'CITY' for cities within a region. Required when 'geo' is provided."
    )


class GoogleTrendsDetailsResponse(BaseModel):
    """Response schema for Google Trends details"""
    query: str
    geo: str
    date: str
    timestamp: str
    interest_over_time: Dict[str, Any]
    related_topics: Dict[str, List[Dict[str, Any]]]
    related_queries: Dict[str, List[Dict[str, Any]]]
    interest_by_region: List[Dict[str, Any]]
    region_drill_down: Optional[Dict[str, Any]] = None


class YouTubeDetailsRequest(BaseModel):
    """Request schema for YouTube video details endpoint"""
    video_id: str = Field(..., description="YouTube video ID")
    country_code: str = Field(
        default="US",
        description="Two-letter country code for context"
    )
    include_comments: bool = Field(
        default=False,
        description="Include top comments for the video"
    )
    max_comments: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of comments to fetch"
    )


class YouTubeDetailsResponse(BaseModel):
    """Response schema for YouTube video details"""
    video_id: str
    timestamp: str
    kind: Optional[str] = None
    etag: Optional[str] = None
    snippet: Dict[str, Any]
    content_details: Dict[str, Any]
    statistics: Dict[str, Any]
    status: Dict[str, Any]
    topic_details: Dict[str, Any]
    player: Dict[str, Any]
    recording_details: Optional[Dict[str, Any]] = None
    available_localizations: List[str] = []
    comments: Optional[List[Dict[str, Any]]] = None
    total_comments: Optional[int] = None


class TikTokDetailsRequest(BaseModel):
    """Request schema for TikTok item details endpoint"""
    item_type: str = Field(
        ...,
        description="Type of TikTok item (hashtag, creator, sound, video)"
    )
    name: str = Field(..., description="Name/title of the item")
    country_code: str = Field(
        default="MY",
        description="Two-letter country code"
    )


class TikTokDetailsResponse(BaseModel):
    """Response schema for TikTok item details"""
    item_type: str
    name: str
    url: Optional[str] = None
    country_code: Optional[str] = None
    rank: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    industry: Optional[Dict[str, Any]] = None
    trending_histogram: Optional[List[Dict[str, Any]]] = None
    related_creators: Optional[List[Dict[str, Any]]] = None
    related_videos: Optional[List[Dict[str, Any]]] = None
    timestamp: str


# ======================= AI ANALYSIS SCHEMAS =======================

class AIAnalysisRequest(BaseModel):
    """Request schema for AI analysis endpoints (interpretation and recommendations)"""
    country_code: str = Field(
        default="US",
        description="Two-letter country code (e.g., 'US', 'MY', 'IN')"
    )
    category: Optional[UnifiedCategory] = Field(
        default=None,
        description="Optional category filter"
    )
    time_range: str = Field(
        default="7d",
        description="Time range: '24h', '7d', '30d', '90d'"
    )