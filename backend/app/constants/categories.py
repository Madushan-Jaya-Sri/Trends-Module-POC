"""
Category mapping configuration for unified category filtering across platforms.

This module provides mappings between unified categories and platform-specific
category identifiers for Google Trends, TikTok, and YouTube.
"""

from typing import Dict, List, Optional
from enum import Enum


class UnifiedCategory(str, Enum):
    """Unified categories that map across all platforms."""
    AUTOMOTIVE = "automotive"
    BEAUTY_FASHION = "beauty_fashion"
    BUSINESS_FINANCE = "business_finance"
    CLIMATE_ENVIRONMENT = "climate_environment"
    ENTERTAINMENT = "entertainment"
    FOOD_DRINK = "food_drink"
    GAMING = "gaming"
    HEALTH_FITNESS = "health_fitness"
    HOBBIES_LIFESTYLE = "hobbies_lifestyle"
    EDUCATION_CAREERS = "education_careers"
    LAW_POLITICS = "law_politics"
    OTHER_MISC = "other_misc"
    PETS_ANIMALS = "pets_animals"
    SCIENCE_TECHNOLOGY = "science_technology"
    SHOPPING = "shopping"
    SPORTS = "sports"
    TRAVEL = "travel"
    ARTS_MEDIA = "arts_media"


# Google Trends Category Mapping (category_id)
GOOGLE_TRENDS_CATEGORIES: Dict[UnifiedCategory, Optional[str]] = {
    UnifiedCategory.AUTOMOTIVE: "1",  # Autos and Vehicles
    UnifiedCategory.BEAUTY_FASHION: "2",  # Beauty and Fashion
    UnifiedCategory.BUSINESS_FINANCE: "3",  # Business and Finance
    UnifiedCategory.CLIMATE_ENVIRONMENT: "20",  # Climate
    UnifiedCategory.ENTERTAINMENT: "4",  # Entertainment
    UnifiedCategory.FOOD_DRINK: "5",  # Food and Drink
    UnifiedCategory.GAMING: "6",  # Games
    UnifiedCategory.HEALTH_FITNESS: "7",  # Health
    UnifiedCategory.HOBBIES_LIFESTYLE: "8",  # Hobbies and Leisure
    UnifiedCategory.EDUCATION_CAREERS: "9",  # Jobs and Education
    UnifiedCategory.LAW_POLITICS: "10",  # Law and Government
    UnifiedCategory.OTHER_MISC: "11",  # Other
    UnifiedCategory.PETS_ANIMALS: "13",  # Pets and Animals
    UnifiedCategory.SCIENCE_TECHNOLOGY: "18",  # Technology (Science is 15, but using 18 for tech focus)
    UnifiedCategory.SHOPPING: "16",  # Shopping
    UnifiedCategory.SPORTS: "17",  # Sports
    UnifiedCategory.TRAVEL: "19",  # Travel and Transportation
    UnifiedCategory.ARTS_MEDIA: None,  # No direct mapping
}


# TikTok Category Mapping (adsHashtagIndustry)
TIKTOK_CATEGORIES: Dict[UnifiedCategory, Optional[str]] = {
    UnifiedCategory.AUTOMOTIVE: "Vehicle & Transportation",
    UnifiedCategory.BEAUTY_FASHION: "Beauty & Personal Care",
    UnifiedCategory.BUSINESS_FINANCE: "Business Services",
    UnifiedCategory.CLIMATE_ENVIRONMENT: None,  # No mapping
    UnifiedCategory.ENTERTAINMENT: "News & Entertainment",
    UnifiedCategory.FOOD_DRINK: "Food & Beverage",
    UnifiedCategory.GAMING: "Games",
    UnifiedCategory.HEALTH_FITNESS: "Health",
    UnifiedCategory.HOBBIES_LIFESTYLE: "Life Services",
    UnifiedCategory.EDUCATION_CAREERS: "Education",
    UnifiedCategory.LAW_POLITICS: None,  # No mapping
    UnifiedCategory.OTHER_MISC: None,  # No mapping
    UnifiedCategory.PETS_ANIMALS: "Pets",
    UnifiedCategory.SCIENCE_TECHNOLOGY: "Tech & Electronics",
    UnifiedCategory.SHOPPING: "Apparel & Accessories",
    UnifiedCategory.SPORTS: "Sports & Outdoor",
    UnifiedCategory.TRAVEL: "Travel",
    UnifiedCategory.ARTS_MEDIA: None,  # No direct mapping
}


# YouTube Category Mapping (videoCategoryId)
# Some unified categories map to multiple YouTube categories
YOUTUBE_CATEGORIES: Dict[UnifiedCategory, Optional[List[str]]] = {
    UnifiedCategory.AUTOMOTIVE: ["2"],  # Autos & Vehicles
    UnifiedCategory.BEAUTY_FASHION: ["26"],  # Howto & Style
    UnifiedCategory.BUSINESS_FINANCE: ["29"],  # Nonprofits & Activism (closest match)
    UnifiedCategory.CLIMATE_ENVIRONMENT: None,  # No direct mapping
    UnifiedCategory.ENTERTAINMENT: ["24"],  # Entertainment
    UnifiedCategory.FOOD_DRINK: ["22"],  # People & Blogs (food content often here)
    UnifiedCategory.GAMING: ["20"],  # Gaming
    UnifiedCategory.HEALTH_FITNESS: ["26"],  # Howto & Style
    UnifiedCategory.HOBBIES_LIFESTYLE: ["22"],  # People & Blogs
    UnifiedCategory.EDUCATION_CAREERS: ["27"],  # Education
    UnifiedCategory.LAW_POLITICS: ["25"],  # News & Politics
    UnifiedCategory.OTHER_MISC: None,  # No mapping
    UnifiedCategory.PETS_ANIMALS: ["15"],  # Pets & Animals
    UnifiedCategory.SCIENCE_TECHNOLOGY: ["28"],  # Science & Technology
    UnifiedCategory.SHOPPING: ["26"],  # Howto & Style
    UnifiedCategory.SPORTS: ["17"],  # Sports
    UnifiedCategory.TRAVEL: ["19"],  # Travel & Events
    UnifiedCategory.ARTS_MEDIA: ["1", "10", "23", "30", "39", "40"],  # Film, Music, Comedy, Movies, etc.
}


# Display names for unified categories
CATEGORY_DISPLAY_NAMES: Dict[UnifiedCategory, str] = {
    UnifiedCategory.AUTOMOTIVE: "Automotive",
    UnifiedCategory.BEAUTY_FASHION: "Beauty & Fashion",
    UnifiedCategory.BUSINESS_FINANCE: "Business & Finance",
    UnifiedCategory.CLIMATE_ENVIRONMENT: "Climate & Environment",
    UnifiedCategory.ENTERTAINMENT: "Entertainment",
    UnifiedCategory.FOOD_DRINK: "Food & Drink",
    UnifiedCategory.GAMING: "Gaming",
    UnifiedCategory.HEALTH_FITNESS: "Health & Fitness",
    UnifiedCategory.HOBBIES_LIFESTYLE: "Hobbies & Lifestyle",
    UnifiedCategory.EDUCATION_CAREERS: "Education & Careers",
    UnifiedCategory.LAW_POLITICS: "Law & Politics",
    UnifiedCategory.OTHER_MISC: "Other / Misc",
    UnifiedCategory.PETS_ANIMALS: "Pets & Animals",
    UnifiedCategory.SCIENCE_TECHNOLOGY: "Science & Technology",
    UnifiedCategory.SHOPPING: "Shopping",
    UnifiedCategory.SPORTS: "Sports",
    UnifiedCategory.TRAVEL: "Travel",
    UnifiedCategory.ARTS_MEDIA: "Arts & Media",
}


def get_google_trends_category(unified_category: UnifiedCategory) -> Optional[str]:
    """Get Google Trends category ID for a unified category."""
    return GOOGLE_TRENDS_CATEGORIES.get(unified_category)


def get_tiktok_category(unified_category: UnifiedCategory) -> Optional[str]:
    """Get TikTok industry name for a unified category."""
    return TIKTOK_CATEGORIES.get(unified_category)


def get_youtube_categories(unified_category: UnifiedCategory) -> Optional[List[str]]:
    """Get YouTube category IDs for a unified category."""
    return YOUTUBE_CATEGORIES.get(unified_category)


def get_youtube_category_string(unified_category: UnifiedCategory) -> Optional[str]:
    """Get YouTube category IDs as comma-separated string for API calls."""
    categories = get_youtube_categories(unified_category)
    return ",".join(categories) if categories else None


def is_category_supported(unified_category: UnifiedCategory, platform: str) -> bool:
    """
    Check if a unified category is supported by a specific platform.

    Args:
        unified_category: The unified category to check
        platform: Platform name ('google', 'tiktok', or 'youtube')

    Returns:
        True if the category is supported by the platform, False otherwise
    """
    if platform.lower() == "google":
        return get_google_trends_category(unified_category) is not None
    elif platform.lower() == "tiktok":
        return get_tiktok_category(unified_category) is not None
    elif platform.lower() == "youtube":
        return get_youtube_categories(unified_category) is not None
    return False


def get_supported_categories(platform: Optional[str] = None) -> List[UnifiedCategory]:
    """
    Get list of supported unified categories.

    Args:
        platform: Optional platform name to filter by ('google', 'tiktok', or 'youtube')
                 If None, returns all unified categories

    Returns:
        List of supported unified categories
    """
    if platform is None:
        return list(UnifiedCategory)

    return [
        category for category in UnifiedCategory
        if is_category_supported(category, platform)
    ]
