from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class TrendContent(BaseModel):
    platform: str
    title: str
    url: Optional[str] = None
    score: float


class TrendRecommendation(BaseModel):
    rank: int
    topic: str
    score: float
    platforms: List[str]
    platform_count: int
    trending_reason: str
    top_content: List[TrendContent]


class TrendsResponse(BaseModel):
    country: str
    generated_at: str
    total_trends: int
    recommendations: List[TrendRecommendation]


class PlatformData(BaseModel):
    platform: str
    data: Dict[str, Any]
    error: Optional[str] = None