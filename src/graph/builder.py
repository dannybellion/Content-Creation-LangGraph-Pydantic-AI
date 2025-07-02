"""
Graph construction and routing logic for the content creation pipeline.
"""

from langgraph.graph import StateGraph, END
from langgraph.types import Command

from src.graph.state import WorkflowState
from src.utils.logging import logger
from src.graph.nodes import (
    parse_brief_node,
    validate_brief_node,
    enhance_brief_node,
    research_node,
    generate_headlines_node,
    select_headline_node,
    make_editorial_decisions_node,
    write_content_node,
    human_review_node,
)


def process_human_feedback(state: WorkflowState) -> str:
    """Process human feedback and decide next action."""
    if not state.human_feedback:
        return "finalize"  # Should not happen, but safety check

    feedback_type = state.human_feedback.feedback_type

    if feedback_type == "approve":
        return "finalize"
    elif feedback_type == "edit_content":
        if state.revision_count >= 3:  # Prevent infinite loops
            return "finalize"
        return "write_content"
    elif feedback_type == "change_plan":
        return "plan_content"
    else:
        return "finalize"  # Default case


def route_after_validation(state: WorkflowState) -> str:
    """Route after validation based on whether user response exists."""
    if state.user_response:
        return "enhance_brief"
    else:
        return "conduct_research"


def create_content_workflow() -> StateGraph:
    """Create and configure the content creation workflow with Cole & Greg framework."""
    workflow = StateGraph(WorkflowState)

    workflow.add_node("parse_brief", parse_brief_node)
    workflow.add_node("validate_brief", validate_brief_node)
    workflow.add_node("enhance_brief", enhance_brief_node)
    workflow.add_node("conduct_research", research_node)
    workflow.add_node("generate_headlines", generate_headlines_node)
    workflow.add_node("select_headline", select_headline_node)
    workflow.add_node(
        "make_editorial_decisions", make_editorial_decisions_node
    )
    workflow.add_node("write_content", write_content_node)
    workflow.add_node("human_review", human_review_node)

    workflow.set_entry_point("parse_brief")

    workflow.add_edge("parse_brief", "validate_brief")
    workflow.add_conditional_edges(
        "validate_brief",
        route_after_validation,
        {
            "enhance_brief": "enhance_brief",
            "conduct_research": "conduct_research",
        },
    )
    workflow.add_edge("enhance_brief", "conduct_research")
    workflow.add_edge("conduct_research", "generate_headlines")
    workflow.add_edge("generate_headlines", "select_headline")
    workflow.add_edge("select_headline", "make_editorial_decisions")
    workflow.add_edge("make_editorial_decisions", "write_content")
    workflow.add_edge("write_content", "human_review")

    workflow.add_conditional_edges(
        "human_review",
        process_human_feedback,
        {
            "finalize": END,
            "write_content": "write_content",
            "plan_content": "make_editorial_decisions",
        },
    )

    return workflow


async def run_content_pipeline(user_input: str) -> WorkflowState:
    """
    Run the complete content creation pipeline.

    Args:
        user_input: Free text content brief from user

    Returns:
        Final workflow state with completed content
    """

    workflow = create_content_workflow()
    app = workflow.compile()

    initial_state = WorkflowState(
        original_input=user_input, current_step="parse_brief"
    )

    logger.info(
        f"Starting content creation pipeline with input: {user_input[:100]}..."
    )

    final_state = None
    async for step in app.astream(initial_state):
        current_node = list(step.keys())[0]
        current_state = step[current_node]
        final_state = current_state

        if hasattr(current_state, "current_step"):
            logger.debug(f"Current step: {current_state.current_step}")

    logger.info("Content creation pipeline completed")

    if final_state:
        final_state.is_complete = True
        final_state.update_step("completed")

    return final_state


async def execute_with_interrupts(
    app, command_or_state, config, interrupt_handler
):
    """
    Recursively execute workflow, handling any depth of interrupts.

    Args:
        app: Compiled LangGraph application
        command_or_state: Initial state or resume command
        config: LangGraph configuration (thread_id, etc.)
        interrupt_handler: Async function to handle interrupts
    """
    async for event in app.astream(command_or_state, config):
        event_name = list(event.keys())[0]
        logger.debug(f"Processing event: {event_name}")

        if event_name == "__interrupt__":
            user_response = await interrupt_handler(app, config)
            await execute_with_interrupts(
                app, Command(resume=user_response), config, interrupt_handler
            )
            break
