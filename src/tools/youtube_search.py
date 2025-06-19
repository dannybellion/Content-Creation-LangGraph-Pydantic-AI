"""YouTube search tool using Apify API with integrated transcript functionality."""

import asyncio
from typing import Optional

from apify_client import ApifyClient
from pydantic import BaseModel
from pydantic_ai import RunContext

from src.config import settings
from src.utils.logging import logger


# Actor IDs for Apify services
YOUTUBE_SEARCH_ACTOR = "h7sDV53CddomktSi5"
TRANSCRIPT_ACTOR = "faVsWy9VTSNVIhWpR"


class YouTubeVideo(BaseModel):
    """Structured representation of a YouTube video."""

    title: str
    url: str
    description: Optional[str] = None
    transcript: Optional[str] = None
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    channel_name: Optional[str] = None


class YouTubeSearchError(Exception):
    """Custom exception for YouTube search errors."""

    pass


async def search_youtube(
    _ctx: RunContext[str], query: str, max_results: int = 3
) -> list[dict[str, any]]:
    """
    Search YouTube videos using Apify API with transcript integration.

    Args:
        query: Search query string
        max_results: Maximum number of videos to return. Default is 3.
        Max 5

    Returns:
        List of video results with title, URL, description, transcript, and metadata
    """
    try:
        videos = await get_youtube_videos(query, max_results)
        return [video.model_dump() for video in videos]
    except Exception as e:
        logger.error(f"YouTube search failed for query '{query}': {e}")
        raise YouTubeSearchError(f"Search failed: {e}") from e


async def get_youtube_videos(
    query: str, max_results: int = 3, client: Optional[ApifyClient] = None
) -> list[YouTubeVideo]:
    """
    Get YouTube videos using Apify API and return structured video objects with transcripts.
    """
    if not settings.apify_api_key or settings.apify_api_key.strip() == "":
        logger.warning("No Apify API key configured, returning empty results")
        return []

    if client is None:
        client = ApifyClient(settings.apify_api_key)

    run_input = {
        "searchQueries": [query],
        "maxResults": max_results,
        "maxResultsShorts": 0,
        "maxResultStreams": 0,
        "startUrls": [],
        "subtitlesLanguage": "any",
        "subtitlesFormat": "srt",
    }

    try:
        logger.info(f"Searching YouTube for: {query}")
        run = client.actor(YOUTUBE_SEARCH_ACTOR).call(run_input=run_input)
        dataset_items = list(
            client.dataset(run["defaultDatasetId"]).iterate_items()
        )

        videos = []
        for item in dataset_items:
            video = _parse_video_item(item)
            if video:
                transcript = await _get_transcript(video.url, client)
                video.transcript = transcript
                videos.append(video)

        logger.info(f"Found {len(videos)} videos for query: {query}")
        return videos[:max_results]

    except Exception as e:
        logger.error(f"YouTube search failed: {e}")
        raise YouTubeSearchError(f"Failed to search YouTube: {e}") from e


def _parse_video_item(item: dict[str, any]) -> Optional[YouTubeVideo]:
    """Parse a video item from Apify response into structured format."""
    try:
        return YouTubeVideo(
            title=item.get("title", "").strip(),
            url=item.get("url", ""),
            description=item.get("description", ""),
            view_count=item.get("viewCount"),
            upload_date=item.get("uploadDate"),
            channel_name=item.get("channelName"),
        )
    except Exception as e:
        logger.warning(f"Failed to parse video item: {e}")
        return None


async def _get_transcript(
    video_url: str, client: Optional[ApifyClient] = None
) -> Optional[str]:
    """
    Get YouTube video transcript using Apify API.

    Args:
        video_url: Full YouTube video URL
        client: Optional ApifyClient instance

    Returns:
        Transcript text or None if failed
    """
    if client is None:
        client = ApifyClient(settings.apify_api_key)

    try:
        run_input = {"videoUrl": video_url}
        run = client.actor(TRANSCRIPT_ACTOR).call(run_input=run_input)
        transcript_items = list(
            client.dataset(run["defaultDatasetId"]).iterate_items()
        )

        if not transcript_items:
            return None

        item = transcript_items[0]

        if "data" in item and isinstance(item["data"], list):
            transcript_segments = [
                segment["text"]
                for segment in item["data"]
                if "text" in segment
            ]
            return " ".join(transcript_segments)

    except Exception as e:
        logger.warning(f"Failed to fetch transcript for {video_url}: {e}")
        return None


if __name__ == "__main__":

    async def test_search():
        videos = await _get_transcript(
            "https://www.youtube.com/watch?v=om-etwwp3Wg&t=6s"
        )
        print(videos)

    asyncio.run(test_search())
