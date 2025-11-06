from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APIFY_API_KEY: str
    YOUTUBE_API_KEY: str
    SERPAPI_API_KEY: str
    OPENAI_API_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()