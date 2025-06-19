from typing import Literal
from pydantic_ai import RunContext
from src.prompts.prompt_manager import PromptManager


async def style_guidelines(
    ctx: RunContext[str],
    content_type: Literal["linkedin"],
) -> str:
    """Get the style guidelines for the content type.

    Args:
        ctx: The run context (not used in this tool but required for consistency)
        content_type: The content type to get the style guidelines for. Available options:
        - "linkedin"

    Returns:
        Style guidelines as a string
    """
    return PromptManager.get_prompt(content_type)
