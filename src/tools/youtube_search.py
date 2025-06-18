"""
YouTube search tool using Apify API with fallback to mock results.
"""

import os
import httpx
import asyncio
from typing import List, Dict, Any


async def search_youtube(query: str, max_results: int = 8) -> List[Dict[str, Any]]:
    """
    Search YouTube videos using Apify API or return mock results for demo.
    
    Args:
        query: Search query string
        max_results: Maximum number of videos to return
        
    Returns:
        List of video results with title, URL, description, and metadata
    """
    api_key = os.getenv("APIFY_API_KEY")
    actor_id = "streamers~youtube-scraper"
    
    async with httpx.AsyncClient() as client:
        # Start the actor run
        run_response = await client.post(
            f"https://api.apify.com/v2/acts/{actor_id}/runs",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "searchKeywords": query,
                "maxResults": max_results,
                "includeVideoTranscripts": True,
                "proxyConfiguration": {"useApifyProxy": True},
            },
            timeout=60.0,
        )
        
        if run_response.status_code == 201:
            run_data = run_response.json()
            run_id = run_data["data"]["id"]
            
            # Wait for completion (with timeout)
            for _ in range(30):  # Wait up to 30 seconds
                await asyncio.sleep(1)
                
                status_response = await client.get(
                    f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    if status_data["data"]["status"] == "SUCCEEDED":
                        # Get results
                        results_response = await client.get(
                            f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}/dataset/items",
                            headers={"Authorization": f"Bearer {api_key}"},
                        )
                        
                        if results_response.status_code == 200:
                            return results_response.json()
                        
                    elif status_data["data"]["status"] in ["FAILED", "ABORTED"]:
                        break
        
                



# Alternative function name for clarity
search_youtube_videos = search_youtube