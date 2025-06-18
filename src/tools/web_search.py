"""
Web search tool using Serper API with fallback to mock results.
"""

import os
import httpx
from typing import List, Dict, Any


async def search_web(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search the web using Serper API or return mock results for demo.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of search results with title, link, snippet, and date
    """
    

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json"
            },
            json={
                "q": query,
                "num": max_results,
                "gl": "us",  # Country
                "hl": "en",  # Language
            },
            timeout=30.0,
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("organic", [])
        else:
            return _get_mock_web_results(query, max_results)


