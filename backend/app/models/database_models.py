from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# ======================= GOOGLE TRENDS DATABASE MODELS =======================

class GoogleTrendsItemDB(BaseModel):
    """Database model for Google Trends item"""
    # Identifiers
    query: str = Field(..., description="The search query text")
    country_code: str = Field(..., description="Country code (e.g., 'US', 'IN')")

    # Trending metadata
    search_volume: Optional[int] = None
    increase_percentage: Optional[int] = None
    active: bool = True
    categories: List[str] = []
    started_ago: Optional[str] = None
    start_timestamp: Optional[int] = None
    end_timestamp: Optional[int] = None

    # Detailed data (populated when user requests details)
    interest_over_time: Optional[List[Dict[str, Any]]] = None
    related_topics_rising: Optional[List[Dict[str, Any]]] = None
    related_topics_top: Optional[List[Dict[str, Any]]] = None
    related_queries_rising: Optional[List[Dict[str, Any]]] = None
    related_queries_top: Optional[List[Dict[str, Any]]] = None
    interest_by_region: Optional[List[Dict[str, Any]]] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    details_fetched_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z'
        }


# ======================= YOUTUBE DATABASE MODELS =======================

class YouTubeVideoDB(BaseModel):
    """Database model for YouTube video"""
    # Identifiers
    video_id: str = Field(..., description="YouTube video ID")
    country_code: str = Field(..., description="Country code where it's trending")

    # Basic metadata
    title: str
    description: str
    channel_id: str
    channel_title: str
    published_at: str
    thumbnail_url: str

    # Statistics
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    favorite_count: int = 0

    # Video details
    duration_sec: int = 0
    tags: List[str] = []
    category_id: str
    default_language: Optional[str] = None
    dimension: str = "2d"
    definition: str = "hd"
    caption: bool = False
    licensed_content: bool = False

    # Detailed data (populated when user requests details)
    detailed_statistics: Optional[Dict[str, Any]] = None
    content_details: Optional[Dict[str, Any]] = None
    snippet_details: Optional[Dict[str, Any]] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    details_fetched_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z'
        }


# ======================= TIKTOK DATABASE MODELS =======================

class TikTokItemDB(BaseModel):
    """Database model for TikTok item (hashtag, creator, sound, or video)"""
    # Identifiers
    item_type: str = Field(..., description="Type: hashtag, creator, sound, or video")
    item_id: Optional[str] = None  # Unique identifier if available
    name: str = Field(..., description="Name or title of the item")
    country_code: str = Field(..., description="Country code")
    url: str = Field(..., description="TikTok URL")

    # Common metadata
    rank: Optional[int] = None

    # Hashtag specific
    video_count: Optional[int] = None
    view_count: Optional[int] = None
    industry_name: Optional[str] = None
    trending_histogram: Optional[List[Dict[str, Any]]] = None
    related_creators: Optional[List[Dict[str, Any]]] = None

    # Creator specific
    follower_count: Optional[int] = None
    liked_count: Optional[int] = None
    avatar: Optional[str] = None
    related_videos: Optional[List[Dict[str, Any]]] = None

    # Sound specific
    author: Optional[str] = None
    duration_sec: Optional[int] = None
    cover_url: Optional[str] = None

    # Video specific
    # (uses duration_sec and cover_url from sound)

    # Detailed data (populated when user requests details)
    detailed_info: Optional[Dict[str, Any]] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    details_fetched_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + 'Z'
        }
