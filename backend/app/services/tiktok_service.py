from apify_client import ApifyClient
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timezone, timedelta
from ..constants import UnifiedCategory, get_tiktok_category

logger = logging.getLogger(__name__)


class TikTokService:
    """Service for fetching TikTok trending data using Apify"""

    def __init__(self, api_key: str):
        self.client = ApifyClient(api_key)
        self.actor_id = "sDvA9jM4WRTDX4Syr"

    def get_trending_data(
        self,
        country_code: str = "MY",
        results_per_page: int = 10,
        time_range: str = "7",
        category: Optional[UnifiedCategory] = None,
        time_period_days: Optional[int] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch trending TikTok data including hashtags, creators, sounds, and videos.

        Args:
            country_code: Two-letter country code (e.g., 'MY', 'US', 'IN')
            results_per_page: Number of results per category
            time_range: Time range in days (default: "7")
            category: Optional unified category to filter trending content
            time_period_days: Optional time period filter in days (1, 7, 30, 90, 120)
                             Maps to TikTok's adsTimeRange or post-filters for 1 day

        Returns:
            Dictionary with separate lists for hashtags, creators, sounds, and videos
        """
        try:
            # Get TikTok-specific industry name from unified category (only if category is provided)
            industry_name = None
            if category is not None:
                industry_name = get_tiktok_category(category)
                if industry_name:
                    logger.info(f"Filtering TikTok trends by category: {category.value} -> {industry_name}")
                else:
                    logger.warning(f"Category {category.value} not supported by TikTok, fetching all categories")
            else:
                logger.info("No category filter specified, fetching all TikTok categories")

            # Determine the adsTimeRange based on time_period_days
            ads_time_range = time_range  # default
            apply_post_filter = False
            post_filter_days = None

            if time_period_days is not None:
                if time_period_days == 1:
                    # For 1 day, fetch 7 days and filter later
                    ads_time_range = "7"
                    apply_post_filter = True
                    post_filter_days = 1
                    logger.info(f"Time period: 1 day - fetching 7 days and will post-filter to 1 day")
                elif time_period_days == 7:
                    ads_time_range = "7"
                    logger.info(f"Time period: 7 days - using native adsTimeRange=7")
                elif time_period_days == 30:
                    ads_time_range = "30"
                    logger.info(f"Time period: 30 days - using native adsTimeRange=30")
                elif time_period_days == 90:
                    ads_time_range = "120"
                    logger.info(f"Time period: 90 days - using adsTimeRange=120")
                elif time_period_days == 120:
                    ads_time_range = "120"
                    logger.info(f"Time period: 120 days - using native adsTimeRange=120")

            run_input = {
                "adsScrapeHashtags": True,
                "resultsPerPage": results_per_page,
                "adsCountryCode": country_code,
                "adsTimeRange": ads_time_range,
                "adsNewOnBoard": True,
                "adsScrapeSounds": True,
                "adsRankType": "popular",
                "adsApprovedForBusinessUse": False,
                "adsScrapeCreators": True,
                "adsSortCreatorsBy": "follower",
                "adsScrapeVideos": True,
                "adsSortVideosBy": "vv",
            }

            # Only add industry filter if category is specified
            if industry_name is not None:
                run_input["adsHashtagIndustry"] = industry_name

            # Run the Actor and wait for it to finish
            run = self.client.actor(self.actor_id).call(run_input=run_input)

            # Fetch results from dataset
            data_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            # Extract and categorize the data
            extracted_data = self._extract_tiktok_data(data_items)

            # Apply post-filtering if needed (for 24 hours / 1 day)
            if apply_post_filter and post_filter_days is not None:
                extracted_data = self._filter_by_time_period(extracted_data, post_filter_days)
                logger.info(f"Post-filtered to {post_filter_days} day(s)")

            logger.info(
                f"Fetched TikTok data for {country_code}: "
                f"{len(extracted_data['hashtags'])} hashtags, "
                f"{len(extracted_data['creators'])} creators, "
                f"{len(extracted_data['sounds'])} sounds, "
                f"{len(extracted_data['videos'])} videos"
            )

            return extracted_data

        except Exception as e:
            logger.error(f"Error fetching TikTok data: {str(e)}")
            return {
                "hashtags": [],
                "creators": [],
                "sounds": [],
                "videos": []
            }

    def _extract_tiktok_data(self, datalist: List[Dict]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract and categorize TikTok data by type.

        Args:
            datalist: Raw data from Apify

        Returns:
            Categorized data dictionary
        """
        hashtags = []
        creators = []
        sounds = []
        videos = []

        for item in datalist:
            item_type = item.get("type")

            # ===================================== HASHTAG =====================================
            if item_type == "hashtag":
                related_creators = []
                for c in item.get("relatedCreators", []):
                    related_creators.append({
                        "nickName": c.get("nickName"),
                        "avatar": c.get("avatar"),
                        "profileUrl": c.get("profileUrl")
                    })

                hashtags.append({
                    "name": item.get("name"),
                    "countryCode": item.get("countryCode"),
                    "rank": item.get("rank"),
                    "trendingHistogram": item.get("trendingHistogram", []),
                    "url": item.get("url"),
                    "videoCount": item.get("videoCount"),
                    "viewCount": item.get("viewCount"),
                    "industryName": item.get("industryName"),
                    "relatedCreators": related_creators
                })

            # ===================================== CREATOR =====================================
            elif item_type == "creator":
                related_videos = []
                for v in item.get("relatedVideos", []):
                    related_videos.append({
                        "webVideoUrl": v.get("webVideoUrl"),
                        "coverUrl": v.get("coverUrl"),
                        "viewCount": v.get("viewCount"),
                        "likedCount": v.get("likedCount"),
                        "createTime": v.get("createTime")
                    })

                creators.append({
                    "avatar": item.get("avatar"),
                    "countryCode": item.get("countryCode"),
                    "followerCount": item.get("followerCount"),
                    "likedCount": item.get("likedCount"),
                    "name": item.get("name"),
                    "url": item.get("url"),
                    "rank": item.get("rank"),
                    "relatedVideos": related_videos
                })

            # ===================================== SOUND =====================================
            elif item_type == "sound":
                sounds.append({
                    "name": item.get("name"),
                    "countryCode": item.get("countryCode"),
                    "rank": item.get("rank"),
                    "trendingHistogram": item.get("trendingHistogram", []),
                    "url": item.get("url"),
                    "coverUrl": item.get("coverUrl"),
                    "durationSec": item.get("durationSec"),
                    "author": item.get("author")
                })

            # ===================================== VIDEO =====================================
            elif item_type == "video":
                videos.append({
                    "countryCode": item.get("countryCode"),
                    "coverUrl": item.get("coverUrl"),
                    "durationSec": item.get("durationSec"),
                    "rank": item.get("rank"),
                    "name": item.get("name"),
                    "url": item.get("url")
                })

        return {
            "hashtags": hashtags,
            "creators": creators,
            "sounds": sounds,
            "videos": videos
        }

    def _filter_by_time_period(
        self,
        data: Dict[str, List[Dict[str, Any]]],
        days: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Filter TikTok data by time period based on trendingHistogram dates.

        Args:
            data: Dictionary containing hashtags, creators, sounds, and videos
            days: Number of days to filter by

        Returns:
            Filtered data dictionary
        """
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(days=days)

        def is_within_period(item: Dict[str, Any]) -> bool:
            """Check if item is within the time period based on trendingHistogram."""
            histogram = item.get('trendingHistogram', [])
            if not histogram:
                # For items without histogram (like some videos/creators), include them
                return True

            try:
                # Check the most recent date in histogram
                date_str = histogram[-1].get('date', '')
                if date_str:
                    item_dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    return item_dt >= cutoff_time
            except Exception as e:
                logger.warning(f"Could not parse trendingHistogram date, error: {str(e)}")
                # Include items with unparseable timestamps to be safe
                return True

            return True

        # Filter each category
        filtered_data = {
            "hashtags": [h for h in data.get('hashtags', []) if is_within_period(h)],
            "creators": data.get('creators', []),  # Creators don't have trendingHistogram
            "sounds": [s for s in data.get('sounds', []) if is_within_period(s)],
            "videos": data.get('videos', [])  # Videos don't have trendingHistogram
        }

        logger.info(
            f"Time period filtered: "
            f"{len(filtered_data['hashtags'])}/{len(data.get('hashtags', []))} hashtags, "
            f"{len(filtered_data['sounds'])}/{len(data.get('sounds', []))} sounds"
        )

        return filtered_data
