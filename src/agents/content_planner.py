from src.agents.base import BaseAgent
from src.models import ContentPlan, WorkflowState
from src.prompts.prompt_manager import PromptManager
from src.tools.web_search import web_search
from src.tools.style_guidelines import style_guidelines

agent = BaseAgent(
    name="content_planner",
    output_type=ContentPlan,
    system_prompt=PromptManager.get_prompt("content_planner_system"),
    model_name="openai:o4-mini",
    temperature=0.1,
    tools=[web_search, style_guidelines],
)


async def create_content_plan(state: WorkflowState) -> ContentPlan:
    """Create a content plan from selected content idea and research findings."""

    planning_prompt = PromptManager.get_prompt(
        "content_planner",
        selected_content_idea=state.selected_content_idea,
        consolidated_research=state.consolidated_research,
        content_brief=state.content_brief,
    )

    return await agent.run(planning_prompt)
