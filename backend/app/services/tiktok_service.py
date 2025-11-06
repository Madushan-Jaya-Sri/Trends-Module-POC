from apify_client import ApifyClient
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class TikTokService:
    def __init__(self, api_key: str):
        self.client = ApifyClient(api_key)
        
    def get_trending_data(self, country_code: str = "US", results_per_page: int = 10) -> Dict[str, Any]:
        """
        Fetch trending TikTok data for a specific country

        Args:
            country_code: Two-letter country code (e.g., 'US', 'GB', 'IN')
            results_per_page: Number of results to fetch

        Returns:
            Dictionary containing hashtags, videos, creators, and sounds
        """
        try:
            run_input = {
                "adsScrapeHashtags": True,
                "resultsPerPage": results_per_page,
                "adsCountryCode": country_code,
                "adsTimeRange": "7",
                "adsNewOnBoard": True,
                "adsScrapeSounds": True,
                "adsRankType": "popular",
                "adsApprovedForBusinessUse": False,
                "adsScrapeCreators": True,
                "adsSortCreatorsBy": "follower",
                "adsScrapeVideos": True,
                "adsSortVideosBy": "vv",
            }

            logger.info(f"Starting TikTok trends scrape for country: {country_code}")
            run = self.client.actor("sDvA9jM4WRTDX4Syr").call(run_input=run_input)

            # Fetch results
            results = {
                "hashtags": [],
                "videos": [],
                "creators": [],
                "sounds": []
            }

            # Categorize items based on their 'type' field
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                item_type = item.get("type", "").lower()

                if item_type == "hashtag":
                    results["hashtags"].append(item)
                elif item_type == "video":
                    results["videos"].append(item)
                elif item_type == "creator":
                    results["creators"].append(item)
                elif item_type == "sound":
                    results["sounds"].append(item)
                else:
                    logger.warning(f"Unknown TikTok item type: {item_type}")

            logger.info(f"TikTok scrape complete. Hashtags: {len(results['hashtags'])}, "
                       f"Videos: {len(results['videos'])}, Creators: {len(results['creators'])}, "
                       f"Sounds: {len(results['sounds'])}")

            return results

        except Exception as e:
            logger.error(f"Error fetching TikTok trends: {str(e)}", exc_info=True)
            return {"hashtags": [], "videos": [], "creators": [], "sounds": [], "error": str(e)}
    
    def extract_topics_from_tiktok(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract topics and keywords from TikTok data
        """
        topics = []

        # Extract from hashtags (field name is 'name')
        for hashtag in data.get("hashtags", [])[:20]:  # Top 20 hashtags
            name = hashtag.get("name", "")
            if name:
                topics.append({
                    "topic": name.replace("#", ""),
                    "source": "hashtag",
                    "views": hashtag.get("viewCount", 0),
                    "videoCount": hashtag.get("videoCount", 0),
                    "rank": hashtag.get("rank", 999),
                    "url": hashtag.get("url", "")
                })

        # Extract from videos (field name is 'name')
        for video in data.get("videos", [])[:20]:  # Top 20 videos
            name = video.get("name", "")
            if name:
                topics.append({
                    "topic": name[:100],  # Limit length
                    "source": "video",
                    "rank": video.get("rank", 999),
                    "url": video.get("url", "")
                })

        # Extract from sounds (field name is 'name')
        for sound in data.get("sounds", [])[:10]:  # Top 10 sounds
            name = sound.get("name", "")
            if name:
                topics.append({
                    "topic": name[:100],
                    "source": "sound",
                    "rank": sound.get("rank", 999),
                    "url": sound.get("url", "")
                })

        return topics