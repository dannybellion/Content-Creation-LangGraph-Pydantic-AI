"""
Simple configuration for the content creation pipeline.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for the content creation pipeline."""

    # OpenAI Configuration
    openai_api_key: str
    default_model: str = "gpt-4.1-nano"

    # Langfuse Configuration
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str

    # External APIs
    apify_api_key: str
    tavily_api_key: str
    youtube_actor_id: str = "streamers-youtube-scraper"


# Create a global settings instance
settings = Settings()
