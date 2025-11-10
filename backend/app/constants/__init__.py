"""Constants package for the Trends Module."""

from .categories import (
    UnifiedCategory,
    GOOGLE_TRENDS_CATEGORIES,
    TIKTOK_CATEGORIES,
    YOUTUBE_CATEGORIES,
    CATEGORY_DISPLAY_NAMES,
    get_google_trends_category,
    get_tiktok_category,
    get_youtube_categories,
    get_youtube_category_string,
    is_category_supported,
    get_supported_categories,
)

__all__ = [
    "UnifiedCategory",
    "GOOGLE_TRENDS_CATEGORIES",
    "TIKTOK_CATEGORIES",
    "YOUTUBE_CATEGORIES",
    "CATEGORY_DISPLAY_NAMES",
    "get_google_trends_category",
    "get_tiktok_category",
    "get_youtube_categories",
    "get_youtube_category_string",
    "is_category_supported",
    "get_supported_categories",
]
