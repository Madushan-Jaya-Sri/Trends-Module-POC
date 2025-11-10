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
from .models.schemas import (
    GoogleTrendsRequest,
    GoogleTrendsResponse,
    TikTokRequest,
    TikTokResponse,
    YouTubeRequest,
    YouTubeResponse
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
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    google_trends_service = None
    tiktok_service = None
    youtube_service = None


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
            "youtube": "initialized" if youtube_service else "error"
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
