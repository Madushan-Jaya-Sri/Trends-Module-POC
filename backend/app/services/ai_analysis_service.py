from typing import Dict, Any, List, AsyncGenerator
import logging
import json
from openai import AsyncOpenAI
from ..config import settings

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Service for AI-powered trend analysis and recommendations using OpenAI"""

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured. AI analysis features will be disabled.")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def stream_trend_interpretation(
        self,
        trends_data: List[Dict[str, Any]],
        country_code: str,
        time_range: str,
        category: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream AI interpretation of trending data.

        Args:
            trends_data: List of trending items with scores
            country_code: Country code
            time_range: Time range of data
            category: Category filter (optional)

        Yields:
            Chunks of AI-generated interpretation
        """
        if not self.client:
            yield "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in your environment."
            return

        try:
            # Prepare context from trends data
            context = self._prepare_trends_context(trends_data, country_code, time_range, category)

            # Create the prompt for interpretation
            prompt = f"""You are a trend analyst. Analyze the following trending data and provide a comprehensive interpretation.

{context}

Please provide a structured interpretation with the following sections:


1. **Overview**: High-level summary of key trends in TWO sentences. 
2. **Executive Summary**: Summary of the overall trend landscape
3. **Key Patterns**: Major patterns and themes identified across platforms
4. **Platform Insights**:
   - Google Trends: What people are searching for
   - YouTube: What content is being watched
   - TikTok: What's viral on social media
5. **Emerging Topics**: New or rapidly growing trends
6. **Audience Behavior**: What this tells us about user interests and behavior
7. **Temporal Analysis**: How trends vary over the {time_range} period

Format your response in clear, structured markdown with bullet points and sections."""

            # Stream the response
            stream = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert trend analyst specializing in social media and search trends. Provide clear, actionable insights in a structured format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream=True,
                temperature=0.7,
                max_tokens=2000
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in stream_trend_interpretation: {str(e)}")
            yield f"\n\nError generating interpretation: {str(e)}"

    async def stream_marketing_recommendations(
        self,
        trends_data: List[Dict[str, Any]],
        country_code: str,
        time_range: str,
        category: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream AI-powered marketing recommendations based on trends.

        Args:
            trends_data: List of trending items with scores
            country_code: Country code
            time_range: Time range of data
            category: Category filter (optional)

        Yields:
            Chunks of AI-generated recommendations
        """
        if not self.client:
            yield "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in your environment."
            return

        try:
            # Prepare context from trends data
            context = self._prepare_trends_context(trends_data, country_code, time_range, category)

            # Create the prompt for recommendations
            prompt = f"""You are a marketing strategist. Based on the following trending data, provide actionable marketing recommendations.

{context}

Please provide strategic marketing recommendations with the following structure:

1. **Content Strategy**:
   - Recommended content themes and topics
   - Platform-specific content ideas
   - Content format recommendations (video, articles, social posts, etc.)

2. **Audience Targeting**:
   - Target audience segments identified from trends
   - Demographics and psychographics insights
   - User intent and motivation analysis

3. **Campaign Ideas**:
   - 3-5 specific campaign concepts based on top trends
   - Cross-platform campaign strategies
   - Timing and scheduling recommendations

4. **SEO & Keywords**:
   - High-priority keywords from Google Trends
   - Content topics for SEO optimization
   - Search intent alignment

5. **Social Media Strategy**:
   - Platform-specific tactics (YouTube, TikTok)
   - Hashtag and creator collaboration opportunities
   - Viral content patterns to leverage

6. **Quick Wins**:
   - Immediate actions to capitalize on current trends
   - Low-effort, high-impact opportunities

7. **Risk Mitigation**:
   - Trends that may be declining or oversaturated
   - Topics to approach with caution

Format your response in clear, actionable markdown with specific examples."""

            # Stream the response
            stream = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert marketing strategist with deep knowledge of digital marketing, social media, and trend-based marketing. Provide specific, actionable recommendations that marketing teams can implement immediately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream=True,
                temperature=0.7,
                max_tokens=2500
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in stream_marketing_recommendations: {str(e)}")
            yield f"\n\nError generating recommendations: {str(e)}"

    def _prepare_trends_context(
        self,
        trends_data: List[Dict[str, Any]],
        country_code: str,
        time_range: str,
        category: str = None
    ) -> str:
        """
        Prepare context string from trends data for LLM.

        Args:
            trends_data: List of trending items
            country_code: Country code
            time_range: Time range
            category: Category filter

        Returns:
            Formatted context string
        """
        # Limit to top 50 trends to avoid token limits
        top_trends = trends_data[:50]

        # Group by platform
        google_trends = [t for t in top_trends if t.get('platform') == 'google_trends']
        youtube_trends = [t for t in top_trends if t.get('platform') == 'youtube']
        tiktok_trends = [t for t in top_trends if t.get('platform') == 'tiktok']

        context_parts = [
            f"**Analysis Context:**",
            f"- Country: {country_code}",
            f"- Time Range: {time_range}",
            f"- Category: {category if category else 'All categories'}",
            f"- Total Trends Analyzed: {len(trends_data)}",
            f"- Top Trends Included: {len(top_trends)}",
            "",
            f"**Platform Distribution:**",
            f"- Google Trends: {len(google_trends)} items",
            f"- YouTube: {len(youtube_trends)} items",
            f"- TikTok: {len(tiktok_trends)} items",
            "",
            "**Top 20 Trending Items:**"
        ]

        # Add top 20 trends with key info
        for i, trend in enumerate(top_trends[:20], 1):
            platform = trend.get('platform', 'unknown')
            title = trend.get('title', trend.get('query', trend.get('name', 'Unknown')))
            score = trend.get('trending_score', 0)

            # Platform-specific metadata
            metadata = ""
            if platform == 'google_trends':
                volume = trend.get('metadata', {}).get('search_volume', 0)
                metadata = f"Search Volume: {volume:,}"
            elif platform == 'youtube':
                views = trend.get('metadata', {}).get('views', 0)
                channel = trend.get('metadata', {}).get('channel', '')
                metadata = f"Views: {views:,}, Channel: {channel}"
            elif platform == 'tiktok':
                entity_type = trend.get('entity_type', '')
                metadata = f"Type: {entity_type}"

            context_parts.append(
                f"{i}. [{platform.upper()}] {title} (Score: {score:.2f}) - {metadata}"
            )

        # Add category distribution if available
        categories = {}
        for trend in top_trends:
            cats = trend.get('categories', [])
            if isinstance(cats, list):
                for cat in cats:
                    # Handle both string and dict categories
                    if isinstance(cat, dict):
                        cat_name = cat.get('name', cat.get('label', str(cat)))
                    else:
                        cat_name = str(cat)
                    categories[cat_name] = categories.get(cat_name, 0) + 1

        if categories:
            context_parts.extend([
                "",
                "**Category Distribution:**"
            ])
            sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]
            for cat, count in sorted_cats:
                context_parts.append(f"- {cat}: {count} items")

        return "\n".join(context_parts)
