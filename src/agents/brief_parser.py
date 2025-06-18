from src.agents.base import BaseAgent
from src.models import ContentBrief
from src.prompts.prompt_manager import PromptManager

agent = BaseAgent(
    name="brief_parser",
    output_type=ContentBrief,
    system_prompt=PromptManager.get_prompt("brief_parser"),
    model_name="gpt-4o",
    temperature=0.1,
)

async def parse_brief(input_text: str) -> ContentBrief:
    """Parse free text input into structured ContentBrief."""
    return await agent.run(input_text)