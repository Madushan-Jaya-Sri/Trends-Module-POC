from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
import logging
from .config import settings

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager"""

    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    def connect(cls):
        """Connect to MongoDB"""
        try:
            if not settings.MONGODB_URI:
                logger.warning("MONGODB_URI not configured, MongoDB features will be disabled")
                cls.client = None
                cls.db = None
                return

            cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
            cls.db = cls.client.get_database("trends_module")
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise

    @classmethod
    def close(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")

    @classmethod
    def get_database(cls):
        """Get database instance"""
        if cls.db is None:
            cls.connect()
        return cls.db

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a specific collection"""
        db = cls.get_database()
        return db[collection_name]


# Collection names
GOOGLE_TRENDS_COLLECTION = "google_trends_items"
YOUTUBE_VIDEOS_COLLECTION = "youtube_videos"
TIKTOK_ITEMS_COLLECTION = "tiktok_items"
UNIFIED_TRENDS_COLLECTION = "unified_trends"


# Database instance
database = Database()


def get_google_trends_collection():
    """Get Google Trends collection"""
    return database.get_collection(GOOGLE_TRENDS_COLLECTION)


def get_youtube_collection():
    """Get YouTube videos collection"""
    return database.get_collection(YOUTUBE_VIDEOS_COLLECTION)


def get_tiktok_collection():
    """Get TikTok items collection"""
    return database.get_collection(TIKTOK_ITEMS_COLLECTION)


def get_unified_trends_collection():
    """Get Unified Trends collection"""
    return database.get_collection(UNIFIED_TRENDS_COLLECTION)
