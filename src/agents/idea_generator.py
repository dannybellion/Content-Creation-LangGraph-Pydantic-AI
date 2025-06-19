from src.agents.base import BaseAgent
from src.models import ContentIdeaOptions, WorkflowState
from src.prompts.prompt_manager import PromptManager

agent = BaseAgent(
    name="idea_generator",
    output_type=ContentIdeaOptions,
    system_prompt=PromptManager.get_prompt("idea_generator_system"),
    model_name="gpt-4.1-mini",
    temperature=0.1,
)


async def generate_content_ideas(state: WorkflowState) -> ContentIdeaOptions:
    """Generate content ideas from validated brief and research."""
    prompt = PromptManager.get_prompt(
        "idea_generator",
        content_brief=state.content_brief,
        consolidated_research=state.consolidated_research,
    )

    return await agent.run(prompt)
