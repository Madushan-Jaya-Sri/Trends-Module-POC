from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from .config import settings
from .services.trends_aggregator import TrendsAggregator
from .models.schemas import TrendsResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Social Media Trends API",
    description="Aggregate trending content from TikTok, YouTube, and Google Trends",
    version="1.0.0"
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
    trends_aggregator = TrendsAggregator(
        apify_key=settings.APIFY_API_KEY,
        youtube_key=settings.YOUTUBE_API_KEY,
        serpapi_key=settings.SERPAPI_API_KEY,
        openai_key=settings.OPENAI_API_KEY
    )
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    trends_aggregator = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Social Media Trends API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "/trends": "Get aggregated trends",
            "/platforms": "Get platform statistics",
            "/health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "services": {
            "aggregator": "initialized" if trends_aggregator else "error"
        }
    }


@app.get("/trends", response_model=TrendsResponse)
async def get_trends(
    country: str = Query(default="US", description="Two-letter country code (e.g., US, GB, IN)"),
    top_n: int = Query(default=20, ge=1, le=50, description="Number of top trends to return")
):
    """
    Get aggregated trending topics from TikTok, YouTube, and Google Trends
    
    - **country**: Two-letter country code (ISO 3166-1 alpha-2)
    - **top_n**: Number of top trending topics to return (1-50)
    
    Returns unified trending recommendations with scores and content from each platform.
    """
    try:
        if not trends_aggregator:
            raise HTTPException(status_code=500, detail="Services not initialized")
        
        logger.info(f"Fetching trends for country: {country}, top_n: {top_n}")
        
        # Get aggregated trends
        result = trends_aggregator.aggregate_trends(country=country.upper(), top_n=top_n)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in get_trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching trends: {str(e)}")


@app.get("/platforms")
async def get_platform_stats(
    country: str = Query(default="US", description="Two-letter country code")
):
    """
    Get statistics about data availability from each platform
    
    - **country**: Two-letter country code
    
    Returns status and count of trending items from each platform.
    """
    try:
        if not trends_aggregator:
            raise HTTPException(status_code=500, detail="Services not initialized")
        
        logger.info(f"Fetching platform stats for country: {country}")
        
        stats = trends_aggregator.get_platform_stats(country=country.upper())
        
        return {
            "country": country.upper(),
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "platforms": stats
        }
        
    except Exception as e:
        logger.error(f"Error in get_platform_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching platform stats: {str(e)}")


@app.get("/countries")
async def get_supported_countries():
    """
    Get list of commonly supported country codes
    
    Returns a list of country codes that work well with all three platforms.
    """
    countries = [
        {"code": "US", "name": "United States"},
        {"code": "GB", "name": "United Kingdom"},
        {"code": "CA", "name": "Canada"},
        {"code": "AU", "name": "Australia"},
        {"code": "IN", "name": "India"},
        {"code": "DE", "name": "Germany"},
        {"code": "FR", "name": "France"},
        {"code": "JP", "name": "Japan"},
        {"code": "BR", "name": "Brazil"},
        {"code": "MX", "name": "Mexico"},
        {"code": "ES", "name": "Spain"},
        {"code": "IT", "name": "Italy"},
        {"code": "KR", "name": "South Korea"},
        {"code": "NL", "name": "Netherlands"},
        {"code": "SE", "name": "Sweden"},
    ]
    
    return {
        "countries": countries,
        "note": "More countries may be supported. These are the most commonly used."
    }


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