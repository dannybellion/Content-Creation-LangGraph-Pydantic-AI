"""
Content creation workflow using LangGraph to orchestrate agents.
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt

from src.models import WorkflowState, HumanFeedback, BriefValidation
from src.agents.brief_parser import parse_brief
from src.agents.brief_validator import validate_brief
from src.agents.content_planner import create_content_plan
from src.agents.researcher import conduct_research
from src.agents.content_writer import write_content, revise_content


# ============================================================================
# Workflow Nodes
# ============================================================================


async def parse_brief_node(state: WorkflowState) -> Dict[str, Any]:
    """Parse free text input into structured ContentBrief."""
    print("🔍 Parsing content brief...")

    brief = await parse_brief(state.original_input)

    return {"content_brief": brief, "current_step": "validate_brief"}


async def validate_brief_node(state: WorkflowState) -> Dict[str, Any]:
    """Validate brief completeness and ask clarifying questions if needed."""
    print("✅ Validating content brief...")

    validation = await validate_brief(state.content_brief)

    # If validation is incomplete, ask for more details
    if not validation.is_complete and validation.clarifying_questions:
        print("\n❓ Need more details to create great content:")
        for i, q in enumerate(validation.clarifying_questions, 1):
            print(f"  {i}. {q.question}")

        # Simple interrupt - just ask for more details
        user_response = interrupt(
            "Please provide more details about your content requirements."
        )

        # Use the brief parser to enhance the brief with additional context
        print("✅ Processing your additional details...")
        enhanced_input = (
            f"{state.original_input}\n\nAdditional details: {user_response}"
        )
        enhanced_brief = await parse_brief(enhanced_input)

        return {
            "content_brief": enhanced_brief,
            "brief_validation": BriefValidation(
                is_complete=True,
                missing_fields=[],
                clarifying_questions=[],
                suggestions=[],
            ),
            "current_step": "plan_content",
        }

    return {"brief_validation": validation, "current_step": "check_validation"}


async def plan_content_node(state: WorkflowState) -> Dict[str, Any]:
    """Create detailed content plan from validated brief."""
    print("📋 Creating content plan...")

    plan = await create_content_plan(state.content_brief)

    return {"content_plan": plan, "current_step": "conduct_research"}


async def research_node(state: WorkflowState) -> Dict[str, Any]:
    """Conduct comprehensive research using web and YouTube sources."""
    print("🔬 Conducting research...")

    research = await conduct_research(state.content_plan)

    return {"consolidated_research": research, "current_step": "write_content"}


async def write_content_node(state: WorkflowState) -> Dict[str, Any]:
    """Write content based on plan and research."""
    print("✍️ Writing content...")

    # Determine if this is initial writing or revision
    if (
        state.human_feedback
        and state.human_feedback.feedback_type == "edit_content"
    ):
        # This is a revision
        content = await revise_content(
            state.draft_content,
            state.human_feedback,
            state.consolidated_research,
        )
        revision_count = state.revision_count + 1
    else:
        # This is initial writing
        content = await write_content(
            state.content_plan,
            state.consolidated_research,
            state.content_brief.brand_guidelines,
        )
        revision_count = state.revision_count

    return {
        "draft_content": content,
        "revision_count": revision_count,
        "current_step": "human_review",
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

    return {"human_feedback": feedback, "current_step": "process_feedback"}


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


# ============================================================================
# Workflow Execution
# ============================================================================


async def run_content_pipeline(
    user_input: str, clarifications: Dict[str, str] = None
) -> WorkflowState:
    """
    Run the complete content creation pipeline.

    Args:
        user_input: Free text content brief from user
        clarifications: Optional answers to clarifying questions

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

    if state.content_plan:
        print(f"📖 Title: {state.content_plan.title}")
        print(f"📊 Target Words: {state.content_plan.estimated_word_count}")

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
    """Create and configure the content creation workflow with interrupts."""
    workflow = StateGraph(WorkflowState)

    # Add all nodes
    workflow.add_node("parse_brief", parse_brief_node)
    workflow.add_node("validate_brief", validate_brief_node)
    workflow.add_node("plan_content", plan_content_node)
    workflow.add_node("conduct_research", research_node)
    workflow.add_node("write_content", write_content_node)
    workflow.add_node("human_review", human_review_node)

    # Set entry point
    workflow.set_entry_point("parse_brief")

    # Define the workflow edges
    workflow.add_edge("parse_brief", "validate_brief")
    workflow.add_edge("validate_brief", "plan_content")
    workflow.add_edge("plan_content", "conduct_research")
    workflow.add_edge("conduct_research", "write_content")
    workflow.add_edge("write_content", "human_review")

    # Conditional: Process human feedback
    workflow.add_conditional_edges(
        "human_review",
        process_human_feedback,
        {
            "finalize": END,
            "write_content": "write_content",
            "plan_content": "plan_content",
        },
    )

    return workflow
