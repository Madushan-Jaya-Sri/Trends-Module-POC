from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    APIFY_API_KEY: str
    YOUTUBE_API_KEY: str
    SERPAPI_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None

    class Config:
        # Look for .env file in the project root (parent of backend directory)
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = True


settings = Settings()