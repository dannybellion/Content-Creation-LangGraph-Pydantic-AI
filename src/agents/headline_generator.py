from src.agents.base import BaseAgent
from src.models.agent_outputs import HeadlineOptions
from src.graph.state import WorkflowState
from src.prompts.prompt_manager import PromptManager

agent = BaseAgent(
    name="headline_generator",
    output_type=HeadlineOptions,
    system_prompt=PromptManager.get_prompt("headline_generator_system"),
    model_name="openai:gpt-4o",
    temperature=0.2,
)


async def generate_headlines(state: WorkflowState) -> HeadlineOptions:
    """Generate multiple headline variations following Cole & Greg framework."""
    prompt = PromptManager.get_prompt(
        "headline_generator",
        content_brief=state.content_brief,
        consolidated_research=state.consolidated_research,
    )

    return await agent.run(prompt)
