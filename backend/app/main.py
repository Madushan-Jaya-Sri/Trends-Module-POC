from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from typing import Optional

from .config import settings
from .services.google_trends_service import GoogleTrendsService
from .services.tiktok_service import TikTokService
from .services.youtube_service import YouTubeService
from .services.trend_aggregator_service import TrendAggregatorService
from .models.schemas import (
    GoogleTrendsRequest,
    GoogleTrendsResponse,
    TikTokRequest,
    TikTokResponse,
    YouTubeRequest,
    YouTubeResponse,
    UnifiedTrendingRequest,
    UnifiedTrendingResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Social Media Trends API",
    description="Fetch trending content from TikTok, YouTube, and Google Trends",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    google_trends_service = GoogleTrendsService(api_key=settings.SERPAPI_API_KEY)
    tiktok_service = TikTokService(api_key=settings.APIFY_API_KEY)
    youtube_service = YouTubeService(api_key=settings.YOUTUBE_API_KEY)
    
    # Initialize aggregator service
    trend_aggregator_service = TrendAggregatorService(
        google_service=google_trends_service,
        tiktok_service=tiktok_service,
        youtube_service=youtube_service
    )
    
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    google_trends_service = None
    tiktok_service = None
    youtube_service = None
    trend_aggregator_service = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Social Media Trends API",
        "version": "2.0.0",
        "status": "active",
        "endpoints": {
            "POST /google-trends": "Get Google Trends data",
            "POST /tiktok-trends": "Get TikTok trending data",
            "POST /youtube-trends": "Get YouTube trending videos",
            "POST /unified-trends": "Get unified trending scores across all platforms",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "services": {
            "google_trends": "initialized" if google_trends_service else "error",
            "tiktok": "initialized" if tiktok_service else "error",
            "youtube": "initialized" if youtube_service else "error",
            "trend_aggregator": "initialized" if trend_aggregator_service else "error"
        }
    }


@app.post("/google-trends", response_model=GoogleTrendsResponse)
async def get_google_trends(request: GoogleTrendsRequest = Body(...)):
    """
    Get trending searches from Google Trends.

    Request body:
    - **country_code**: Two-letter country code (e.g., 'US', 'IN', 'LK')
    - **category**: Optional unified category to filter trends

    Returns trending searches with timestamps, search volumes, and trending durations.
    """
    try:
        if not google_trends_service:
            raise HTTPException(status_code=500, detail="Google Trends service not initialized")

        logger.info(f"Fetching Google Trends for country: {request.country_code}, category: {request.category}")

        trends = google_trends_service.get_trending_now(
            country_code=request.country_code,
            category=request.category
        )

        return GoogleTrendsResponse(
            country=request.country_code,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            total_trends=len(trends),
            trending_searches=trends
        )

    except Exception as e:
        logger.error(f"Error in get_google_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching Google Trends: {str(e)}")


@app.post("/tiktok-trends", response_model=TikTokResponse)
async def get_tiktok_trends(request: TikTokRequest = Body(...)):
    """
    Get trending data from TikTok including hashtags, creators, sounds, and videos.

    Request body:
    - **country_code**: Two-letter country code (e.g., 'MY', 'US', 'IN')
    - **results_per_page**: Number of results per category (default: 10)
    - **time_range**: Time range in days (default: "7")
    - **category**: Unified category to filter trending content (default: Shopping)

    Returns categorized trending data from TikTok.
    """
    try:
        if not tiktok_service:
            raise HTTPException(status_code=500, detail="TikTok service not initialized")

        logger.info(f"Fetching TikTok trends for country: {request.country_code}, category: {request.category}")

        data = tiktok_service.get_trending_data(
            country_code=request.country_code,
            results_per_page=request.results_per_page,
            time_range=request.time_range,
            category=request.category
        )

        return TikTokResponse(
            country=request.country_code,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            hashtags=data["hashtags"],
            creators=data["creators"],
            sounds=data["sounds"],
            videos=data["videos"],
            total_items={
                "hashtags": len(data["hashtags"]),
                "creators": len(data["creators"]),
                "sounds": len(data["sounds"]),
                "videos": len(data["videos"])
            }
        )

    except Exception as e:
        logger.error(f"Error in get_tiktok_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching TikTok trends: {str(e)}")


@app.post("/youtube-trends", response_model=YouTubeResponse)
async def get_youtube_trends(request: YouTubeRequest = Body(...)):
    """
    Get trending videos from YouTube.

    Request body:
    - **country_code**: Two-letter country code (e.g., 'US', 'MY', 'IN')
    - **max_results**: Maximum number of videos to fetch (default: 10, max: 50)
    - **category**: Optional unified category to filter videos

    Returns trending YouTube videos with comprehensive metadata.
    """
    try:
        if not youtube_service:
            raise HTTPException(status_code=500, detail="YouTube service not initialized")

        logger.info(f"Fetching YouTube trends for country: {request.country_code}, category: {request.category}")

        videos = youtube_service.get_trending_videos(
            country_code=request.country_code,
            max_results=request.max_results,
            category=request.category
        )

        return YouTubeResponse(
            country=request.country_code,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            total_videos=len(videos),
            videos=videos
        )

    except Exception as e:
        logger.error(f"Error in get_youtube_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching YouTube trends: {str(e)}")


@app.post("/unified-trends", response_model=UnifiedTrendingResponse)
async def get_unified_trends(request: UnifiedTrendingRequest = Body(...)):
    """
    Get unified trending data across all platforms with universal scoring.
    
    This endpoint aggregates data from Google Trends, YouTube, and TikTok,
    calculates a universal trending score for each item, and returns the
    top trends sorted by score.
    
    **Scoring Methodology:**
    - Volume (30%): Raw reach and visibility metrics
    - Engagement (25%): Quality of user interactions
    - Velocity (20%): Speed of growth and viral potential
    - Recency (15%): Time relevance with exponential decay
    - Cross-Platform (10%): Presence across multiple platforms
    
    Request body:
    - **country_code**: Two-letter country code (e.g., 'US', 'MY', 'IN')
    - **category**: Optional unified category filter
    - **max_results_per_platform**: Results to fetch from each platform (default: 10)
    - **time_range**: Optional time filter: '1h', '24h', '7d', '30d', '3m', '6m', '1y'
    - **limit**: Number of top trends to return (default: 25)
    
    Returns top trending items across all platforms with calculated scores.
    """
    try:
        if not trend_aggregator_service:
            raise HTTPException(status_code=500, detail="Trend aggregator service not initialized")
        
        logger.info(
            f"Fetching unified trends for country: {request.country_code}, "
            f"category: {request.category}, time_range: {request.time_range}"
        )
        
        # Step 1: Aggregate data from all platforms
        aggregated_data = trend_aggregator_service.aggregate_all_trends(
            country_code=request.country_code,
            category=request.category,
            max_results=request.max_results_per_platform
        )
        
        trends = aggregated_data['trends']
        platform_counts = aggregated_data['platform_counts']
        
        logger.info(f"Aggregated {len(trends)} trends from all platforms")
        
        # Step 2: Filter by time range if specified
        if request.time_range:
            trends = trend_aggregator_service.filter_by_time_range(
                trends=trends,
                time_range=request.time_range
            )
            logger.info(f"After time filtering: {len(trends)} trends remain")
        
        # Step 3: Calculate universal trending scores
        scored_trends = trend_aggregator_service.calculate_trending_scores(trends)
        
        logger.info("Calculated trending scores for all items")
        
        # Step 4: Limit to top N results
        top_trends = scored_trends[:request.limit]
        
        # Step 5: Prepare metadata for response
        for trend in top_trends:
            # Extract relevant metadata based on platform
            metadata = {}
            
            if trend['platform'] == 'google_trends':
                metadata = {
                    'search_volume': trend.get('search_volume', 0),
                    'increase_percentage': trend.get('increase_percentage', 0),
                    'active': trend.get('active', True),
                    'categories': trend.get('categories', []),
                    'started_ago': trend.get('started_ago', '')
                }
            
            elif trend['platform'] == 'youtube':
                metadata = {
                    'channel': trend.get('channelTitle', ''),
                    'views': trend.get('viewCount', 0),
                    'likes': trend.get('likeCount', 0),
                    'comments': trend.get('commentCount', 0),
                    'duration_sec': trend.get('duration_sec', 0),
                    'thumbnail': trend.get('thumbnail', ''),
                    'published_at': trend.get('publishedAt', '')
                }
            
            elif trend['platform'] == 'tiktok':
                entity_type = trend.get('entity_type', '')
                
                if entity_type == 'hashtag':
                    metadata = {
                        'views': trend.get('viewCount', 0),
                        'videos': trend.get('videoCount', 0),
                        'industry': trend.get('industryName', ''),
                        'rank': trend.get('rank', 0)
                    }
                elif entity_type == 'creator':
                    metadata = {
                        'followers': trend.get('followerCount', 0),
                        'total_likes': trend.get('likedCount', 0),
                        'avatar': trend.get('avatar', ''),
                        'rank': trend.get('rank', 0)
                    }
                elif entity_type == 'sound':
                    metadata = {
                        'author': trend.get('author', ''),
                        'duration_sec': trend.get('durationSec', 0),
                        'cover_url': trend.get('coverUrl', ''),
                        'rank': trend.get('rank', 0)
                    }
                elif entity_type == 'video':
                    metadata = {
                        'duration_sec': trend.get('durationSec', 0),
                        'cover_url': trend.get('coverUrl', ''),
                        'rank': trend.get('rank', 0)
                    }
            
            trend['metadata'] = metadata
        
        # Remove raw_data to reduce response size (optional)
        for trend in top_trends:
            if 'raw_data' in trend:
                del trend['raw_data']
        
        return UnifiedTrendingResponse(
            country=request.country_code,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            time_range=request.time_range,
            total_trends_analyzed=len(scored_trends),
            returned_trends=len(top_trends),
            platform_counts=platform_counts,
            score_methodology={
                "weights": {
                    "volume": 0.30,
                    "engagement": 0.25,
                    "velocity": 0.20,
                    "recency": 0.15,
                    "cross_platform": 0.10
                },
                "description": "Universal trending score combines volume, engagement, velocity, recency, and cross-platform presence",
                "scale": "0-100 (higher is better)",
                "normalization": "Min-max normalization within dataset"
            },
            trends=top_trends
        )
    
    except Exception as e:
        logger.error(f"Error in get_unified_trends: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching unified trends: {str(e)}")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)