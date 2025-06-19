from src.agents.base import BaseAgent
from src.models import ContentPlan, WorkflowState
from src.prompts.prompt_manager import PromptManager
from src.tools.style_guidelines import style_guidelines

agent = BaseAgent(
    name="content_editor",
    output_type=ContentPlan,
    system_prompt=PromptManager.get_prompt("content_editor_system"),
    model_name="openai:o4-mini",
    temperature=0.1,
    tools=[style_guidelines],
)


async def make_editorial_decisions(state: WorkflowState) -> ContentPlan:
    """Make high-leverage editorial decisions and create strategic content plan."""
    prompt = PromptManager.get_prompt(
        "content_editor",
        content_brief=state.content_brief,
        consolidated_research=state.consolidated_research,
        selected_headline_variation=state.selected_headline_variation,
    )

    return await agent.run(prompt)
