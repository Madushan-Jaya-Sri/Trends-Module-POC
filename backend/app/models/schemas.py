from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ======================= GOOGLE TRENDS SCHEMAS =======================

class GoogleTrendsRequest(BaseModel):
    """Request schema for Google Trends endpoint"""
    country_code: str = Field(
        default="US",
        description="Two-letter country code (e.g., 'US', 'IN', 'LK')"
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
        description="Time range in days"
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
