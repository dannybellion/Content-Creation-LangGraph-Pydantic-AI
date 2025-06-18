from src.agents.base import BaseAgent
from src.models import ConsolidatedResearch, ContentPlan, DraftContent, HumanFeedback
from src.prompts.prompt_manager import PromptManager

agent = BaseAgent(
    name="content_writer",
    output_type=DraftContent,
    system_prompt=PromptManager.get_prompt("content_writer"),
    model_name="claude-3-5-sonnet-20241022",
    temperature=0.4,
    tools=[_analyze_readability, _check_keyword_density],
)

async def write_content(content_plan: ContentPlan, research: ConsolidatedResearch, brand_guidelines: str = None) -> DraftContent:
    """Write content based on plan and research."""
    writing_prompt = f"""
    Write high-quality content based on this plan and research:

    CONTENT PLAN:
    Title: {content_plan.title}
    Outline: {content_plan.outline}
    Key Messages: {content_plan.key_messages}
    Target Keywords: {content_plan.target_keywords}
    Estimated Word Count: {content_plan.estimated_word_count}
    Unique Value Proposition: {content_plan.unique_value_proposition}

    RESEARCH INSIGHTS:
    Key Insights: {research.key_insights}
    Unique Angles: {research.unique_angles}
    Expert Quotes: {research.expert_quotes}
    Statistics: {research.statistics}
    Trending Topics: {research.trending_topics}

    BRAND GUIDELINES: {brand_guidelines or "Professional, authoritative tone"}

    Write content that provides real value and actionable insights to readers.
    Use the available tools to ensure quality and optimization.
    """
    
    return await agent.run(writing_prompt)

async def revise_content(current_content: DraftContent, feedback: HumanFeedback, research: ConsolidatedResearch = None) -> DraftContent:
    """Revise content based on human feedback."""
    revision_prompt = f"""
    Revise this content based on human feedback:

    CURRENT CONTENT:
    Title: {current_content.title}
    Content: {current_content.content}
    Word Count: {current_content.word_count}

    HUMAN FEEDBACK:
    Type: {feedback.feedback_type}
    Comments: {feedback.comments}
    Requested Changes: {feedback.requested_changes}
    Elements to Preserve: {feedback.preserve_elements}

    Apply the requested changes while maintaining content quality and SEO optimization.
    """
    
    return await agent.run(revision_prompt)