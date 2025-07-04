from src.agents.base import BaseAgent
from src.models.agent_outputs import ConsolidatedResearch
from src.graph.state import WorkflowState
from src.prompts.prompt_manager import PromptManager
from src.tools.web_search import web_search


agent = BaseAgent(
    name="researcher",
    output_type=ConsolidatedResearch,
    system_prompt=PromptManager.get_prompt("researcher_system"),
    model_name="openai:gpt-4o-mini",
    temperature=0.1,
    tools=[web_search],
)


async def conduct_research(state: WorkflowState) -> ConsolidatedResearch:
    """Conduct comprehensive research using both web and YouTube sources."""
    research_prompt = PromptManager.get_prompt(
        "researcher",
        topic=state.content_brief.topic,
        key_points=state.content_brief.key_points,
        target_audience=state.content_brief.target_audience,
        call_to_action=state.content_brief.call_to_action,
    )

    return await agent.run(research_prompt)
