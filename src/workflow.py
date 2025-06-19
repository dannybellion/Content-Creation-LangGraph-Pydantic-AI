"""
Content creation workflow using LangGraph to orchestrate agents.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command

from src.models import WorkflowState, HumanFeedback, BriefValidation
from src.agents.brief_parser import parse_brief
from src.agents.brief_validator import validate_brief
from src.agents.headline_generator import generate_headlines
from src.agents.content_editor import make_editorial_decisions
from src.agents.researcher import conduct_research
from src.agents.content_writer import write_content, revise_content


# ============================================================================
# Workflow Nodes
# ============================================================================


async def parse_brief_node(state: WorkflowState) -> Dict[str, Any]:
    """Parse free text input into structured ContentBrief."""
    print("🔍 Parsing content brief...")

    brief = await parse_brief(state.original_input)

    return {"content_brief": brief}


async def validate_brief_node(state: WorkflowState) -> Dict[str, Any]:
    """Validate brief completeness and ask clarifying questions if needed."""
    print("✅ Validating content brief...")

    validation = await validate_brief(state.content_brief)

    if not validation.is_complete and validation.clarifying_questions:
        user_response = interrupt(validation.clarifying_questions)

        return {
            "brief_validation": validation,
            "user_response": user_response,
        }

    return {"brief_validation": validation}


async def enhance_brief_node(state: WorkflowState) -> Dict[str, Any]:
    """Enhance brief with user response and re-parse."""
    print("✅ Processing your additional details...")

    # Combine original input with user response
    enhanced_input = (
        f"{state.original_input}\n\nAdditional details: {state.user_response}"
    )
    enhanced_brief = await parse_brief(enhanced_input)

    return {
        "content_brief": enhanced_brief,
        "brief_validation": BriefValidation(
            is_complete=True,
            missing_fields=[],
            clarifying_questions="",
            suggestions=[],
        ),
    }


async def research_node(state: WorkflowState) -> Dict[str, Any]:
    """Conduct comprehensive research using web and YouTube sources."""
    print("🔬 Conducting research...")

    research = await conduct_research(state)

    return {"consolidated_research": research}


async def generate_headlines_node(state: WorkflowState) -> Dict[str, Any]:
    """Generate multiple headline variations following Cole & Greg framework."""
    print("📰 Generating strategic headline variations...")

    headline_options = await generate_headlines(state)

    return {"headline_options": headline_options}


async def select_headline_node(state: WorkflowState) -> Dict[str, Any]:
    """Present headline variations for human selection."""
    print("🎯 Presenting headline variations for selection...")

    headlines = state.headline_options

    print("\n📰 TOP HEADLINE RECOMMENDATIONS:")
    for i, idx in enumerate(headlines.recommended_top_3, 1):
        variation = headlines.variations[idx]
        print(f"\n{i}. {variation.headline}")
        print(f"   Hook Strength: {variation.hook_strength}/10")
        print(f"   Audience Fit: {variation.target_audience_fit}/10")
        print("   Main Points:")
        for j, point in enumerate(variation.main_points, 1):
            print(f"     {j}. {point}")

    user_choice = interrupt(
        "Please select which headline you'd like to proceed with (1, 2, or 3):"
    )

    try:
        choice_index = int(user_choice.strip()) - 1
        if 0 <= choice_index < len(headlines.recommended_top_3):
            selected_idx = headlines.recommended_top_3[choice_index]
            selected_headline = headlines.variations[selected_idx]
        else:
            selected_idx = headlines.recommended_top_3[0]
            selected_headline = headlines.variations[selected_idx]
    except (ValueError, IndexError):
        selected_idx = headlines.recommended_top_3[0]
        selected_headline = headlines.variations[selected_idx]

    return {"selected_headline_variation": selected_headline}


async def make_editorial_decisions_node(
    state: WorkflowState,
) -> Dict[str, Any]:
    """Make high-leverage editorial decisions and create strategic content plan."""
    print("🎭 Making editorial decisions and strategic planning...")

    content_plan = await make_editorial_decisions(state)

    return {"content_plan": content_plan}


async def write_content_node(state: WorkflowState) -> Dict[str, Any]:
    """Write content based on plan and research."""
    print("✍️ Writing content...")

    if (
        state.human_feedback
        and state.human_feedback.feedback_type == "edit_content"
    ):
        content = await revise_content(state)
        revision_count = state.revision_count + 1
    else:
        content = await write_content(state)
        revision_count = state.revision_count

    return {
        "draft_content": content,
        "revision_count": revision_count,
    }


async def human_review_node(state: WorkflowState) -> Dict[str, Any]:
    """Present content for human review and collect feedback."""
    print("👥 Content ready for human review...")

    content = state.draft_content

    print("\n📄 CONTENT PREVIEW:")
    print(f"Title: {content.title}")
    print(f"Word Count: {content.word_count}")
    print(f"Preview: {content.content[:200]}...")

    user_feedback = interrupt(
        f"Please review this content:\n\nTitle: {content.title}\nWord Count: {content.word_count}\nPreview: {content.content[:300]}...\n\nYour feedback (or say 'approve' to finish):"
    )

    if "approve" in user_feedback.lower():
        feedback = HumanFeedback(
            feedback_type="approve",
            comments=user_feedback,
            requested_changes=[],
            preserve_elements=[],
        )
    else:
        feedback = HumanFeedback(
            feedback_type="edit_content",
            comments=user_feedback,
            requested_changes=[
                user_feedback
            ],
            preserve_elements=[],
        )

    return {"human_feedback": feedback}


# ============================================================================
# Decision Functions (for conditional edges)
# ============================================================================


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


# ============================================================================
# Workflow Execution
# ============================================================================


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

    print("🚀 Starting content creation pipeline...")
    print(f"📝 Input: {user_input[:100]}...")

    final_state = None
    async for step in app.astream(initial_state):
        current_node = list(step.keys())[0]
        current_state = step[current_node]
        final_state = current_state

        if hasattr(current_state, "current_step"):
            print(f"📍 Current step: {current_state.current_step}")

    print("✅ Content creation pipeline completed!")

    if final_state:
        final_state.is_complete = True
        final_state.update_step("completed")

    return final_state



# ============================================================================
# Workflow Creation
# ============================================================================


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
    workflow.add_edge(
        "conduct_research", "generate_headlines"
    )
    workflow.add_edge(
        "generate_headlines", "select_headline"
    )
    workflow.add_edge(
        "select_headline", "make_editorial_decisions"
    )
    workflow.add_edge(
        "make_editorial_decisions", "write_content"
    )
    workflow.add_edge("write_content", END)
    workflow.add_edge("write_content", "human_review")

    workflow.add_conditional_edges(
        "human_review",
        process_human_feedback,
        {
            "finalize": END,
            "write_content": "write_content",
            "plan_content": "plan_content"
        }
    )

    return workflow


async def execute_with_interrupts(app, command_or_state, config, interrupt_handler):
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
        print(f"📍 Event: {event_name}")
        
        if event_name == "__interrupt__":
            user_response = await interrupt_handler(app, config)
            await execute_with_interrupts(app, Command(resume=user_response), config, interrupt_handler)
            break
