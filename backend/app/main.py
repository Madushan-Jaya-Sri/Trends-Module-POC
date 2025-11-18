from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import logging
from datetime import datetime
from typing import Optional

from .config import settings
from .database import database
from .auth import get_current_user, User
from .services.google_trends_service import GoogleTrendsService
from .services.tiktok_service import TikTokService
from .services.youtube_service import YouTubeService
from .services.trend_aggregator_service import TrendAggregatorService
from .services.google_trends_details_service import GoogleTrendsDetailsService
from .services.youtube_details_service import YouTubeDetailsService
from .services.tiktok_details_service import TikTokDetailsService
from .services.data_storage_service import DataStorageService
from .services.ai_analysis_service import AIAnalysisService
from .models.schemas import (
    GoogleTrendsRequest,
    GoogleTrendsResponse,
    TikTokRequest,
    TikTokResponse,
    YouTubeRequest,
    YouTubeResponse,
    UnifiedTrendingRequest,
    UnifiedTrendingResponse,
    GoogleTrendsDetailsRequest,
    GoogleTrendsDetailsResponse,
    YouTubeDetailsRequest,
    YouTubeDetailsResponse,
    TikTokDetailsRequest,
    TikTokDetailsResponse,
    AIAnalysisRequest
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


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize MongoDB connection on startup"""
    try:
        database.connect()
        logger.info("MongoDB connection initialized")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    try:
        database.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {str(e)}")

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

    # Initialize details services
    google_trends_details_service = GoogleTrendsDetailsService(api_key=settings.SERPAPI_API_KEY)
    youtube_details_service = YouTubeDetailsService(api_key=settings.YOUTUBE_API_KEY)
    tiktok_details_service = TikTokDetailsService()
    data_storage_service = DataStorageService()
    ai_analysis_service = AIAnalysisService()

    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    google_trends_service = None
    tiktok_service = None
    youtube_service = None
    trend_aggregator_service = None
    google_trends_details_service = None
    youtube_details_service = None
    tiktok_details_service = None
    data_storage_service = None
    ai_analysis_service = None


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
            "POST /google-trends/details": "Get detailed Google Trends analysis",
            "POST /youtube/details": "Get detailed YouTube video information",
            "POST /tiktok/details": "Get detailed TikTok item information",
            "POST /ai-interpretation": "Get AI-powered trend interpretation (streaming)",
            "POST /ai-recommendations": "Get AI-powered marketing recommendations (streaming)",
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
            "trend_aggregator": "initialized" if trend_aggregator_service else "error",
            "google_trends_details": "initialized" if google_trends_details_service else "error",
            "youtube_details": "initialized" if youtube_details_service else "error",
            "tiktok_details": "initialized" if tiktok_details_service else "error",
            "data_storage": "initialized" if data_storage_service else "error"
        }
    }


@app.post("/google-trends", response_model=GoogleTrendsResponse)
async def get_google_trends(
    request: GoogleTrendsRequest = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Get trending searches from Google Trends.

    Request body:
    - **country_code**: Two-letter country code (e.g., 'US', 'IN', 'LK')
    - **category**: Optional unified category to filter trends
    - **time_period**: Time period filter ('4h', '24h', '48h', '7d')

    Returns trending searches with timestamps, search volumes, and trending durations.

    Requires authentication via Bearer token in Authorization header.
    """
    try:
        if not google_trends_service:
            raise HTTPException(status_code=500, detail="Google Trends service not initialized")

        logger.info(f"User {user.user_id} fetching Google Trends for country: {request.country_code}, category: {request.category}, time_period: {request.time_period}")

        # Map time_period to hours parameter
        hours = None
        if request.time_period:
            time_period_map = {
                '4h': 4,
                '24h': 24,
                '48h': 48,
                '7d': 168
            }
            hours = time_period_map.get(request.time_period)

        trends = google_trends_service.get_trending_now(
            country_code=request.country_code,
            category=request.category,
            hours=hours
        )

        # Store Google Trends items in MongoDB for future reference (async operation)
        if data_storage_service:
            try:
                for trend in trends:
                    await data_storage_service.store_google_trends_item(
                        query=trend.get("query"),
                        country_code=request.country_code,
                        trend_data=trend,
                        user_id=user.user_id
                    )
                logger.info(f"Stored {len(trends)} Google Trends items in MongoDB for user {user.user_id}")
            except Exception as storage_error:
                logger.warning(f"Failed to store Google Trends items in MongoDB: {str(storage_error)}")

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
async def get_tiktok_trends(
    request: TikTokRequest = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Get trending data from TikTok including hashtags, creators, sounds, and videos.

    Request body:
    - **country_code**: Two-letter country code (e.g., 'MY', 'US', 'IN')
    - **results_per_page**: Number of results per category (default: 10)
    - **time_range**: Time range in days (deprecated - use time_period instead)
    - **time_period**: Time period filter ('7d', '30d', '120d')
    - **category**: Unified category to filter trending content (default: Shopping)

    Returns categorized trending data from TikTok.

    Requires authentication via Bearer token in Authorization header.
    """
    try:
        if not tiktok_service:
            raise HTTPException(status_code=500, detail="TikTok service not initialized")

        logger.info(f"User {user.user_id} fetching TikTok trends for country: {request.country_code}, category: {request.category}, time_period: {request.time_period}")

        # Map time_period to days parameter
        time_period_days = None
        if request.time_period:
            time_period_map = {
                '7d': 7,
                '30d': 30,
                '120d': 120
            }
            time_period_days = time_period_map.get(request.time_period)

        # Build kwargs for TikTok service
        tiktok_kwargs = {
            "country_code": request.country_code,
            "results_per_page": request.results_per_page,
            "time_range": request.time_range,
            "time_period_days": time_period_days
        }

        # Only add category if it's not None
        if request.category is not None:
            tiktok_kwargs["category"] = request.category

        data = tiktok_service.get_trending_data(**tiktok_kwargs)

        # Store TikTok items in MongoDB for future reference (async operation)
        if data_storage_service:
            try:
                # Store hashtags
                for hashtag in data.get("hashtags", []):
                    await data_storage_service.store_tiktok_item(
                        item_type="hashtag",
                        name=hashtag.get("name"),
                        country_code=request.country_code,
                        item_data=hashtag,
                        user_id=user.user_id
                    )

                # Store creators
                for creator in data.get("creators", []):
                    await data_storage_service.store_tiktok_item(
                        item_type="creator",
                        name=creator.get("name"),
                        country_code=request.country_code,
                        item_data=creator,
                        user_id=user.user_id
                    )

                # Store sounds
                for sound in data.get("sounds", []):
                    await data_storage_service.store_tiktok_item(
                        item_type="sound",
                        name=sound.get("name"),
                        country_code=request.country_code,
                        item_data=sound,
                        user_id=user.user_id
                    )

                # Store videos
                for video in data.get("videos", []):
                    await data_storage_service.store_tiktok_item(
                        item_type="video",
                        name=video.get("name"),
                        country_code=request.country_code,
                        item_data=video,
                        user_id=user.user_id
                    )

                logger.info(f"Stored TikTok items in MongoDB for user {user.user_id}: {len(data['hashtags'])} hashtags, {len(data['creators'])} creators, {len(data['sounds'])} sounds, {len(data['videos'])} videos")
            except Exception as storage_error:
                logger.warning(f"Failed to store TikTok items in MongoDB: {str(storage_error)}")

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
async def get_youtube_trends(
    request: YouTubeRequest = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Get trending videos from YouTube.

    Request body:
    - **country_code**: Two-letter country code (e.g., 'US', 'MY', 'IN')
    - **max_results**: Maximum number of videos to fetch (default: 10, max: 50)
    - **category**: Optional unified category to filter videos
    - **time_period**: Time period filter ('1d', '7d', '30d', '90d')

    Returns trending YouTube videos with comprehensive metadata.

    Requires authentication via Bearer token in Authorization header.
    """
    try:
        if not youtube_service:
            raise HTTPException(status_code=500, detail="YouTube service not initialized")

        logger.info(f"User {user.user_id} fetching YouTube trends for country: {request.country_code}, category: {request.category}, time_period: {request.time_period}")

        # Map time_period to days parameter
        time_period_days = None
        if request.time_period:
            time_period_map = {
                '1d': 1,
                '7d': 7,
                '30d': 30,
                '90d': 90
            }
            time_period_days = time_period_map.get(request.time_period)

        videos = youtube_service.get_trending_videos(
            country_code=request.country_code,
            max_results=request.max_results,
            category=request.category,
            time_period_days=time_period_days
        )

        # Store YouTube videos in MongoDB for future reference (async operation)
        if data_storage_service:
            try:
                for video in videos:
                    await data_storage_service.store_youtube_video(
                        video_id=video.get("id"),
                        country_code=request.country_code,
                        video_data=video,
                        user_id=user.user_id
                    )
                logger.info(f"Stored {len(videos)} YouTube videos in MongoDB for user {user.user_id}")
            except Exception as storage_error:
                logger.warning(f"Failed to store YouTube videos in MongoDB: {str(storage_error)}")

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
async def get_unified_trends(
    request: UnifiedTrendingRequest = Body(...),
    user: User = Depends(get_current_user)
):
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
    - **time_range**: Time filter: '24h' (24 hours), '7d' (7 days - default), '30d' (30 days), '90d' (90 days)
    - **limit**: Number of top trends to return (default: 25)

    Returns top trending items across all platforms with calculated scores.

    Requires authentication via Bearer token in Authorization header.
    """
    try:
        if not trend_aggregator_service:
            raise HTTPException(status_code=500, detail="Trend aggregator service not initialized")

        logger.info(
            f"User {user.user_id} fetching unified trends for country: {request.country_code}, "
            f"category: {request.category}, time_range: {request.time_range}"
        )

        # Step 1: Aggregate data from all platforms with optimized pre-filtering
        aggregated_data = trend_aggregator_service.aggregate_all_trends(
            country_code=request.country_code,
            category=request.category,
            max_results=request.max_results_per_platform,
            time_period=request.time_range
        )

        trends = aggregated_data['trends']
        platform_counts = aggregated_data['platform_counts']

        logger.info(f"Aggregated {len(trends)} trends from all platforms (with pre-filtering)")

        # Step 2: Calculate universal trending scores
        scored_trends = trend_aggregator_service.calculate_trending_scores(trends)
        
        logger.info("Calculated trending scores for all items")

        # Step 3: Limit to top N results
        top_trends = scored_trends[:request.limit]

        # Step 4: Prepare metadata for response
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

        # Store unified trends snapshot in MongoDB
        if data_storage_service:
            try:
                category_value = request.category.value if request.category else None
                await data_storage_service.store_unified_trends(
                    country_code=request.country_code,
                    category=category_value,
                    time_range=request.time_range,
                    trends_data=top_trends,
                    user_id=user.user_id
                )
                logger.info(f"Stored unified trends snapshot for user {user.user_id}: {len(top_trends)} trends for {request.country_code}")
            except Exception as storage_error:
                logger.warning(f"Failed to store unified trends in MongoDB: {str(storage_error)}")

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


@app.post("/google-trends/details", response_model=GoogleTrendsDetailsResponse)
async def get_google_trends_details(
    request: GoogleTrendsDetailsRequest = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Get detailed Google Trends analysis for a specific search query.

    This endpoint provides comprehensive Google Trends data including:
    - Interest over time with timeline data
    - Related topics (rising and top)
    - Related queries (rising and top)
    - Interest by region (country/state/province level)
    - Optional city-level drill-down for specific regions

    Request body:
    - **query**: Search query to analyze (required)
    - **country_code**: Two-letter country code (default: 'US')
    - **date**: Time period (e.g., 'today 12-m', 'today 3-m', 'today 1-m')
    - **include_region_drill_down**: Include city-level data for top 3 regions (default: False)
    - **geo**: Geographic code for specific region drill-down (e.g., 'LK-1')
    - **region_level**: Region level ('REGION' or 'CITY') when geo is provided

    Returns comprehensive Google Trends analysis or specific region drill-down data.

    Requires authentication via Bearer token in Authorization header.
    """
    try:
        if not google_trends_details_service:
            raise HTTPException(status_code=500, detail="Google Trends details service not initialized")

        # Check if this is a region drill-down request (city-level data for specific region)
        if request.geo and request.region_level:
            logger.info(
                f"User {user.user_id} fetching city-level drill-down for query: '{request.query}', "
                f"geo: {request.geo}, region_level: {request.region_level}"
            )

            # Fetch only city-level data for the specified region
            city_data = google_trends_details_service.get_interest_by_region(
                query=request.query,
                geo=request.geo,
                region_level=request.region_level,
                date=request.date
            )

            # Store city-level drill-down data in MongoDB
            try:
                # Retrieve existing document and update with city data
                existing_doc = await data_storage_service.get_google_trends_item(
                    query=request.query,
                    country_code=request.country_code,
                    user_id=user.user_id
                )

                if existing_doc:
                    # Add city-level data to region_drill_down field
                    if "region_drill_down" not in existing_doc or existing_doc["region_drill_down"] is None:
                        existing_doc["region_drill_down"] = {}
                    existing_doc["region_drill_down"][request.geo] = city_data

                    # Update the document
                    await data_storage_service.store_google_trends_item(
                        query=request.query,
                        country_code=request.country_code,
                        trend_data=existing_doc,
                        user_id=user.user_id
                    )
                    logger.info(f"Stored city-level drill-down data for {request.geo} in MongoDB for user {user.user_id}")
            except Exception as storage_error:
                logger.warning(f"Failed to store city-level drill-down data: {str(storage_error)}")

            # Return response with drill-down data
            details = {
                "query": request.query,
                "geo": request.geo,
                "date": request.date,
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "interest_over_time": {},
                "related_topics": {"rising": [], "top": []},
                "related_queries": {"rising": [], "top": []},
                "interest_by_region": city_data,
                "region_drill_down": {request.geo: city_data}
            }

            return GoogleTrendsDetailsResponse(**details)

        else:
            # Fetch complete details (standard request)
            logger.info(
                f"User {user.user_id} fetching Google Trends details for query: '{request.query}', "
                f"country: {request.country_code}, date: {request.date}"
            )

            details = google_trends_details_service.get_complete_details(
                query=request.query,
                geo=request.country_code,
                date=request.date,
                include_region_drill_down=request.include_region_drill_down
            )

            # Store in MongoDB for future reference (async operation)
            try:
                await data_storage_service.store_google_trends_item(
                    query=request.query,
                    country_code=request.country_code,
                    trend_data=details,  # Pass all details
                    user_id=user.user_id
                )
            except Exception as storage_error:
                logger.warning(f"Failed to store Google Trends details in MongoDB: {str(storage_error)}")

            return GoogleTrendsDetailsResponse(**details)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_google_trends_details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching Google Trends details: {str(e)}")


@app.post("/youtube/details", response_model=YouTubeDetailsResponse)
async def get_youtube_details(
    request: YouTubeDetailsRequest = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Get detailed information for a specific YouTube video.

    This endpoint provides comprehensive YouTube video data including:
    - Complete snippet (title, description, channel, tags, etc.)
    - Content details (duration, definition, dimension, captions)
    - Statistics (views, likes, comments, etc.)
    - Status information (privacy, embeddability, etc.)
    - Topic details and categories
    - Player embed information
    - Optional: Top comments

    Request body:
    - **video_id**: YouTube video ID (required)
    - **country_code**: Two-letter country code for context (default: 'US')
    - **include_comments**: Include top comments (default: False)
    - **max_comments**: Maximum number of comments to fetch (default: 20, max: 100)

    Returns comprehensive YouTube video details.

    Requires authentication via Bearer token in Authorization header.
    """
    try:
        if not youtube_details_service:
            raise HTTPException(status_code=500, detail="YouTube details service not initialized")

        logger.info(
            f"User {user.user_id} fetching YouTube details for video: {request.video_id}, "
            f"country: {request.country_code}, include_comments: {request.include_comments}"
        )

        # Fetch complete details
        details = youtube_details_service.get_complete_details(
            video_id=request.video_id,
            include_comments=request.include_comments,
            max_comments=request.max_comments
        )

        if "error" in details:
            raise HTTPException(status_code=404, detail=details["error"])

        # Store in MongoDB for future reference (async operation)
        try:
            await data_storage_service.store_youtube_video(
                video_id=request.video_id,
                country_code=request.country_code,
                video_data=details,  # Pass all details
                user_id=user.user_id
            )
        except Exception as storage_error:
            logger.warning(f"Failed to store YouTube video in MongoDB: {str(storage_error)}")

        return YouTubeDetailsResponse(**details)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_youtube_details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching YouTube details: {str(e)}")


@app.post("/tiktok/details", response_model=TikTokDetailsResponse)
async def get_tiktok_details(
    request: TikTokDetailsRequest = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Get detailed information for a specific TikTok item.

    This endpoint provides organized TikTok item details based on type:
    - **Hashtag**: Views, videos, industry, trending histogram, related creators
    - **Creator**: Followers, total likes, avatar, related videos
    - **Sound**: Author, duration, cover URL, trending histogram
    - **Video**: Duration, cover URL, basic metadata

    Request body:
    - **item_type**: Type of item ('hashtag', 'creator', 'sound', 'video') - required
    - **name**: Name/title of the item (required)
    - **country_code**: Two-letter country code (default: 'MY')

    Note: This endpoint requires the item to have been previously fetched
    via the /tiktok-trends endpoint and stored in the database.

    Returns organized TikTok item details.

    Requires authentication via Bearer token in Authorization header.
    """
    try:
        if not tiktok_details_service or not data_storage_service:
            raise HTTPException(status_code=500, detail="TikTok details service not initialized")

        logger.info(
            f"User {user.user_id} fetching TikTok details for {request.item_type}: '{request.name}', "
            f"country: {request.country_code}"
        )

        # Retrieve item from MongoDB
        stored_item = await data_storage_service.get_tiktok_item(
            item_type=request.item_type,
            name=request.name,
            country_code=request.country_code,
            user_id=user.user_id
        )

        if not stored_item:
            raise HTTPException(
                status_code=404,
                detail=f"TikTok {request.item_type} '{request.name}' not found in database. "
                       "Please fetch trending TikTok data first using /tiktok-trends endpoint."
            )

        # Organize details using the details service
        details = tiktok_details_service.get_item_details(
            item_data=stored_item,
            item_type=request.item_type
        )

        if "error" in details:
            raise HTTPException(status_code=500, detail=details["error"])

        return TikTokDetailsResponse(**details)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_tiktok_details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching TikTok details: {str(e)}")


# ======================= AI ANALYSIS ENDPOINTS =======================

@app.post("/ai-interpretation")
async def get_ai_interpretation(
    request: AIAnalysisRequest = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Get AI-powered interpretation of trending data with streaming response.

    This endpoint analyzes unified trends data from MongoDB and provides structured insights
    including patterns, platform-specific insights, emerging topics, and audience behavior.

    Request body:
    - **country_code**: Two-letter country code (default: 'US')
    - **category**: Optional category filter
    - **time_range**: Time range: '24h', '7d', '30d', '90d' (default: '7d')

    Returns streaming text response with AI-generated interpretation in markdown format.

    Requires authentication via Bearer token in Authorization header.
    """
    try:
        if not ai_analysis_service:
            raise HTTPException(status_code=500, detail="AI analysis service not initialized")

        if not data_storage_service:
            raise HTTPException(status_code=500, detail="Data storage service not initialized")

        logger.info(
            f"User {user.user_id} requesting AI interpretation for {request.country_code}, "
            f"category: {request.category}, time_range: {request.time_range}"
        )

        # Retrieve latest unified trends data for this user
        category_value = request.category.value if request.category else None
        trends_snapshot = await data_storage_service.get_latest_unified_trends(
            country_code=request.country_code,
            user_id=user.user_id,
            category=category_value,
            time_range=request.time_range
        )

        if not trends_snapshot or not trends_snapshot.get('trends'):
            raise HTTPException(
                status_code=404,
                detail=f"No trends data found for {request.country_code} with the specified filters. "
                       "Please fetch unified trends first using /unified-trends endpoint."
            )

        trends_data = trends_snapshot.get('trends', [])
        logger.info(f"Found {len(trends_data)} trends for AI interpretation")

        # Stream the AI interpretation
        async def generate_interpretation():
            async for chunk in ai_analysis_service.stream_trend_interpretation(
                trends_data=trends_data,
                country_code=request.country_code,
                time_range=request.time_range,
                category=category_value
            ):
                yield chunk

        return StreamingResponse(
            generate_interpretation(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"  # Disable buffering for nginx
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_ai_interpretation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating AI interpretation: {str(e)}")


@app.post("/ai-recommendations")
async def get_ai_recommendations(
    request: AIAnalysisRequest = Body(...),
    user: User = Depends(get_current_user)
):
    """
    Get AI-powered marketing recommendations based on trending data with streaming response.

    This endpoint analyzes unified trends data and provides actionable marketing recommendations
    including content strategy, audience targeting, campaign ideas, SEO keywords, and social media tactics.

    Request body:
    - **country_code**: Two-letter country code (default: 'US')
    - **category**: Optional category filter
    - **time_range**: Time range: '24h', '7d', '30d', '90d' (default: '7d')

    Returns streaming text response with AI-generated marketing recommendations in markdown format.

    Requires authentication via Bearer token in Authorization header.
    """
    try:
        if not ai_analysis_service:
            raise HTTPException(status_code=500, detail="AI analysis service not initialized")

        if not data_storage_service:
            raise HTTPException(status_code=500, detail="Data storage service not initialized")

        logger.info(
            f"User {user.user_id} requesting AI recommendations for {request.country_code}, "
            f"category: {request.category}, time_range: {request.time_range}"
        )

        # Retrieve latest unified trends data for this user
        category_value = request.category.value if request.category else None
        trends_snapshot = await data_storage_service.get_latest_unified_trends(
            country_code=request.country_code,
            user_id=user.user_id,
            category=category_value,
            time_range=request.time_range
        )

        if not trends_snapshot or not trends_snapshot.get('trends'):
            raise HTTPException(
                status_code=404,
                detail=f"No trends data found for {request.country_code} with the specified filters. "
                       "Please fetch unified trends first using /unified-trends endpoint."
            )

        trends_data = trends_snapshot.get('trends', [])
        logger.info(f"Found {len(trends_data)} trends for AI recommendations")

        # Stream the AI recommendations
        async def generate_recommendations():
            async for chunk in ai_analysis_service.stream_marketing_recommendations(
                trends_data=trends_data,
                country_code=request.country_code,
                time_range=request.time_range,
                category=category_value
            ):
                yield chunk

        return StreamingResponse(
            generate_recommendations(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"  # Disable buffering for nginx
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_ai_recommendations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating AI recommendations: {str(e)}")


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