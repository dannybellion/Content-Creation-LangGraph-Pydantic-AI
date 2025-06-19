from src.agents.base import BaseAgent
from src.models import BriefValidation, ContentBrief
from src.prompts.prompt_manager import PromptManager
from src.config import settings

agent = BaseAgent(
    name="brief_validator",
    output_type=BriefValidation,
    system_prompt=PromptManager.get_prompt("brief_validator"),
    model_name="openai:gpt-4.1-mini",
    temperature=0.1,
)


async def validate_brief(brief: ContentBrief) -> BriefValidation:
    """Validate a ContentBrief and return validation results."""
    validation_prompt = f"""
    Please validate this content brief for completeness:

    Topic: {brief.topic}
    Target Audience: {brief.target_audience}
    Content Type: {brief.content_type}
    Tone: {brief.tone}
    Word Count Target: {brief.word_count_target}
    Key Points: {brief.key_points}
    Call to Action: {brief.call_to_action}

    Analyze this brief and determine if there's sufficient information to create high-quality content.
    """

    return await agent.run(validation_prompt)
