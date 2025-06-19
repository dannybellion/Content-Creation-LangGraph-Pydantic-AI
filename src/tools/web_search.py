from pydantic_ai import RunContext
from tavily import TavilyClient
from src.config import settings

from src.utils.logging import log_data


async def web_search(ctx: RunContext[str], query: str) -> str:
    """Search the web for information using Tavily API.

    Args:
        ctx: The run context (not used in this tool but required for consistency)
        query: The search query to find relevant information

    Returns:
        Formatted search results as a string with titles, URLs, and content snippets
    """
    log_data("Tavily API call", query)

    client = TavilyClient(settings.tavily_api_key)
    response = client.search(
        query=query,
        search_depth="basic",
        max_results=5,
    )

    return str(response)
