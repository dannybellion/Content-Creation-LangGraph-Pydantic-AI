from src.agents.base import BaseAgent
from src.models.agent_outputs import BriefValidation, ContentBrief
from src.prompts.prompt_manager import PromptManager

agent = BaseAgent(
    name="brief_validator",
    output_type=BriefValidation,
    system_prompt=PromptManager.get_prompt("brief_validator"),
    model_name="openai:gpt-4o-mini",
    temperature=0.1,
)


async def validate_brief(brief: ContentBrief) -> BriefValidation:
    """Validate a ContentBrief for Cole & Greg framework readiness."""
    validation_prompt = f"""
    Validate this content brief for strategic content creation readiness:

    {brief}

    Determine if we have sufficient information to execute the Cole & Greg framework for high-leverage content decisions.
    """

    return await agent.run(validation_prompt)
