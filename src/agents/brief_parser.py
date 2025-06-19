from src.agents.base import BaseAgent
from src.models import ContentBrief
from src.prompts.prompt_manager import PromptManager
from src.config import settings

agent = BaseAgent(
    name="brief_parser",
    output_type=ContentBrief,
    system_prompt=PromptManager.get_prompt("brief_parser"),
    model_name="openai:gpt-4.1-mini",
    temperature=0.1,
)


async def parse_brief(input_text: str) -> ContentBrief:
    """Parse free text input into structured ContentBrief."""
    return await agent.run(input_text)
