"""
Content creation workflow using LangGraph to orchestrate agents.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt

from src.models import WorkflowState, HumanFeedback, BriefValidation
from src.agents.brief_parser import parse_brief
from src.agents.brief_validator import validate_brief

# Note: idea_generator removed in favor of direct headline generation per Cole & Greg framework
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

    # If validation is incomplete, ask for more details
    if not validation.is_complete and validation.clarifying_questions:
        print(validation.clarifying_questions)

        # Simple interrupt - just ask for more details
        user_response = interrupt(
            "Please provide more details about your content requirements."
        )

        # Store user response and route to enhanced parsing
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


# Note: idea generation and selection removed per Cole & Greg framework
# Headlines ARE the content ideas, so we go directly from research to headline generation


async def generate_headlines_node(state: WorkflowState) -> Dict[str, Any]:
    """Generate multiple headline variations following Cole & Greg framework."""
    print("📰 Generating strategic headline variations...")

    headline_options = await generate_headlines(state)

    return {"headline_options": headline_options}


async def select_headline_node(state: WorkflowState) -> Dict[str, Any]:
    """Present headline variations for human selection."""
    print("🎯 Presenting headline variations for selection...")

    headlines = state.headline_options

    # Display top headline recommendations
    print("\n📰 TOP HEADLINE RECOMMENDATIONS:")
    for i, idx in enumerate(headlines.recommended_top_3, 1):
        variation = headlines.variations[idx]
        print(f"\n{i}. {variation.headline}")
        print(f"   Hook Strength: {variation.hook_strength}/10")
        print(f"   Audience Fit: {variation.target_audience_fit}/10")
        print("   Main Points:")
        for j, point in enumerate(variation.main_points, 1):
            print(f"     {j}. {point}")

    # Get user selection
    user_choice = interrupt(
        "Please select which headline you'd like to proceed with (1, 2, or 3):"
    )

    # Parse user choice and get selected headline
    try:
        choice_index = int(user_choice.strip()) - 1
        if 0 <= choice_index < len(headlines.recommended_top_3):
            selected_idx = headlines.recommended_top_3[choice_index]
            selected_headline = headlines.variations[selected_idx]
        else:
            # Default to first recommendation if invalid choice
            selected_idx = headlines.recommended_top_3[0]
            selected_headline = headlines.variations[selected_idx]
    except (ValueError, IndexError):
        # Default to first recommendation if parsing fails
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


# Note: plan_content_node has been replaced by make_editorial_decisions_node
# which follows the Cole & Greg framework for high-leverage decision making


async def write_content_node(state: WorkflowState) -> Dict[str, Any]:
    """Write content based on plan and research."""
    print("✍️ Writing content...")

    # Determine if this is initial writing or revision
    if (
        state.human_feedback
        and state.human_feedback.feedback_type == "edit_content"
    ):
        # This is a revision
        content = await revise_content(state)
        revision_count = state.revision_count + 1
    else:
        # This is initial writing
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

    # Show content preview
    print("\n📄 CONTENT PREVIEW:")
    print(f"Title: {content.title}")
    print(f"Word Count: {content.word_count}")
    print(f"Preview: {content.content[:200]}...")

    # Simple interrupt for content review
    user_feedback = interrupt(
        f"Please review this content:\n\nTitle: {content.title}\nWord Count: {content.word_count}\nPreview: {content.content[:300]}...\n\nYour feedback (or say 'approve' to finish):"
    )

    # Create feedback object - let LLM determine if it's approval or changes needed
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
            ],  # Use the full feedback as requested changes
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

    # Create workflow
    workflow = create_content_workflow()
    app = workflow.compile()

    # Initialize state
    initial_state = WorkflowState(
        original_input=user_input, current_step="parse_brief"
    )

    print("🚀 Starting content creation pipeline...")
    print(f"📝 Input: {user_input[:100]}...")

    # Execute workflow
    final_state = None
    async for step in app.astream(initial_state):
        # Get the current state
        current_node = list(step.keys())[0]
        current_state = step[current_node]
        final_state = current_state

        # Print progress
        if hasattr(current_state, "current_step"):
            print(f"📍 Current step: {current_state.current_step}")

    print("✅ Content creation pipeline completed!")

    # Mark as complete if we reached the end
    if final_state:
        final_state.is_complete = True
        final_state.update_step("completed")

    return final_state


def print_workflow_summary(state: WorkflowState) -> None:
    """Print a summary of the workflow execution."""
    print("\n" + "=" * 50)
    print("CONTENT CREATION SUMMARY")
    print("=" * 50)

    if state.content_brief:
        print(f"📋 Topic: {state.content_brief.topic}")
        print(f"🎯 Audience: {state.content_brief.target_audience}")
        print(f"📝 Type: {state.content_brief.content_type}")

    # Note: Content idea selection removed - headlines ARE the content ideas

    if state.selected_headline_variation:
        print(
            f"📰 Selected Headline: {state.selected_headline_variation.headline}"
        )
        print(
            f"📊 Hook Strength: {state.selected_headline_variation.hook_strength}/10"
        )

    if state.content_plan:
        print(f"📖 Strategic Title: {state.content_plan.selected_headline}")
        print(
            f"🎯 Container Type: {state.content_plan.content_container.container_type}"
        )
        print(
            f"✨ Magical Way: {state.content_plan.content_container.magical_way}"
        )
        print(
            f"🎯 Tangible Value Score: {state.content_plan.tangible_value_score}/10"
        )

    if state.consolidated_research:
        print(
            f"🔬 Research Quality: {state.consolidated_research.research_quality_score}"
        )
        print(
            f"📚 Key Insights: {len(state.consolidated_research.key_insights)}"
        )

    if state.draft_content:
        print(f"✍️ Final Word Count: {state.draft_content.word_count}")
        print(f"🔄 Revisions: {state.revision_count}")

    print(f"⏰ Status: {'Completed' if state.is_complete else 'In Progress'}")
    print("=" * 50)


# ============================================================================
# Workflow Creation
# ============================================================================


def create_content_workflow() -> StateGraph:
    """Create and configure the content creation workflow with Cole & Greg framework."""
    workflow = StateGraph(WorkflowState)

    # Add all nodes
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
    # workflow.add_node("human_review", human_review_node)

    # Set entry point
    workflow.set_entry_point("parse_brief")

    # Define the workflow edges (updated for Cole & Greg framework)
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
    )  # Direct from research to headlines per Cole & Greg framework
    workflow.add_edge(
        "generate_headlines", "select_headline"
    )  # New: Human selects best headline
    workflow.add_edge(
        "select_headline", "make_editorial_decisions"
    )  # New: Strategic planning with selected headline
    workflow.add_edge(
        "make_editorial_decisions", "write_content"
    )  # Editorial decisions feed into writing
    workflow.add_edge("write_content", END)  # Complete workflow after writing
    #
    # workflow.add_edge("write_content", "human_review")

    # Conditional: Process human feedback
    # workflow.add_conditional_edges(
    #     "human_review",
    #     process_human_feedback,
    #     {
    #         "finalize": END,
    #         "write_content": "write_content",
    #         "plan_content": "plan_content"
    #     }
    # )

    return workflow
