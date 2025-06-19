from src.agents.base import BaseAgent
from src.models import (
    DraftContent,
    WorkflowState,
)
from src.prompts.prompt_manager import PromptManager
from src.tools.content_analysis import (
    analyze_readability,
    check_keyword_density,
)
from src.tools.web_search import web_search

agent = BaseAgent(
    name="content_writer",
    output_type=DraftContent,
    system_prompt=PromptManager.get_prompt("content_writer_system"),
    model_name="anthropic:claude-4-sonnet-20250514",
    temperature=0.1,
    tools=[analyze_readability, check_keyword_density, web_search],
)


async def write_content(state: WorkflowState) -> DraftContent:
    """Write content based on plan and research."""
    writing_prompt = PromptManager.get_prompt(
        "content_writer",
        selected_content_idea=state.selected_content_idea,
        content_plan=state.content_plan,
        consolidated_research=state.consolidated_research,
        content_brief=state.content_brief,
        human_feedback=None,
        current_content=None,
    )

    return await agent.run(writing_prompt)


async def revise_content(
    state: WorkflowState,
) -> DraftContent:
    """Revise content based on human feedback."""
    revision_prompt = PromptManager.get_prompt(
        "content_writer",
        selected_content_idea=state.selected_content_idea,
        content_plan=state.content_plan,
        consolidated_research=state.consolidated_research,
        content_brief=state.content_brief,
        human_feedback=state.human_feedback,
        current_content=state.draft_content,
    )

    return await agent.run(revision_prompt)
