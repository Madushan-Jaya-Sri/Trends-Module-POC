from apify_client import ApifyClient
from typing import List, Dict, Any
import logging

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
        time_range: str = "7"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch trending TikTok data including hashtags, creators, sounds, and videos.

        Args:
            country_code: Two-letter country code (e.g., 'MY', 'US', 'IN')
            results_per_page: Number of results per category
            time_range: Time range in days (default: "7")

        Returns:
            Dictionary with separate lists for hashtags, creators, sounds, and videos
        """
        try:
            run_input = {
                "adsScrapeHashtags": True,
                "resultsPerPage": results_per_page,
                "adsCountryCode": country_code,
                "adsTimeRange": time_range,
                "adsNewOnBoard": True,
                "adsScrapeSounds": True,
                "adsRankType": "popular",
                "adsApprovedForBusinessUse": False,
                "adsScrapeCreators": True,
                "adsSortCreatorsBy": "follower",
                "adsScrapeVideos": True,
                "adsSortVideosBy": "vv",
            }

            # Run the Actor and wait for it to finish
            run = self.client.actor(self.actor_id).call(run_input=run_input)

            # Fetch results from dataset
            data_items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())

            # Extract and categorize the data
            extracted_data = self._extract_tiktok_data(data_items)

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
