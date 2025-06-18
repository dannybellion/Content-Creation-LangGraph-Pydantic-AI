from src.agents.base import BaseAgent
from src.models import ContentPlan, ContentBrief
from src.prompts.prompt_manager import PromptManager

agent = BaseAgent(
    name="content_planner",
    output_type=ContentPlan,
    system_prompt=PromptManager.get_prompt("content_planner"),
    model_name="gpt-4o",
    temperature=0.3,
)

async def create_content_plan(brief: ContentBrief) -> ContentPlan:
    """Create a content plan from a validated brief."""
    planning_prompt = f"""
    Create a comprehensive content plan for:

    Topic: {brief.topic}
    Target Audience: {brief.target_audience}
    Content Type: {brief.content_type}
    Tone: {brief.tone}
    Target Word Count: {brief.word_count_target}
    Key Points to Cover: {brief.key_points}
    SEO Keywords: {brief.seo_keywords}
    Call to Action: {brief.call_to_action}
    Brand Guidelines: {brief.brand_guidelines}

    Create a detailed plan that will result in engaging, valuable content for the target audience.
    """
    
    return await agent.run(planning_prompt)