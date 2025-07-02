"""
Workflow node functions for the content creation pipeline.
"""

from typing import Any
from langgraph.types import interrupt

from src.graph.state import WorkflowState, HumanFeedback
from src.utils.logging import logger
from src.models.agent_outputs import BriefValidation
from src.agents import (
    parse_brief,
    validate_brief,
    generate_headlines,
    make_editorial_decisions,
    conduct_research,
    write_content,
    revise_content,
)


async def parse_brief_node(state: WorkflowState) -> dict[str, Any]:
    """Parse free text input into structured ContentBrief."""
    logger.info("Parsing content brief")

    brief = await parse_brief(state.original_input)

    return {"content_brief": brief}


async def validate_brief_node(state: WorkflowState) -> dict[str, Any]:
    """Validate brief completeness and ask clarifying questions if needed."""
    logger.info("Validating content brief")

    validation = await validate_brief(state.content_brief)

    if not validation.is_complete and validation.clarifying_questions:
        user_response = interrupt(validation.clarifying_questions)

        return {
            "brief_validation": validation,
            "user_response": user_response,
        }

    return {"brief_validation": validation}


async def enhance_brief_node(state: WorkflowState) -> dict[str, Any]:
    """Enhance brief with user response and re-parse."""
    logger.info("Processing additional user details")

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


async def research_node(state: WorkflowState) -> dict[str, Any]:
    """Conduct comprehensive research using web and YouTube sources."""
    logger.info("Conducting research")

    research = await conduct_research(state)

    return {"consolidated_research": research}


async def generate_headlines_node(state: WorkflowState) -> dict[str, Any]:
    """Generate multiple headline variations following Cole & Greg framework."""
    logger.info("Generating strategic headline variations")

    headline_options = await generate_headlines(state)

    return {"headline_options": headline_options}


async def select_headline_node(state: WorkflowState) -> dict[str, Any]:
    """Present headline variations for human selection."""
    logger.info("Presenting headline variations for selection")

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
) -> dict[str, Any]:
    """Make high-leverage editorial decisions and create strategic content plan."""
    logger.info("Making editorial decisions and strategic planning")

    content_plan = await make_editorial_decisions(state)

    return {"content_plan": content_plan}


async def write_content_node(state: WorkflowState) -> dict[str, Any]:
    """Write content based on plan and research."""
    logger.info("Writing content")

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


async def human_review_node(state: WorkflowState) -> dict[str, Any]:
    """Present content for human review and collect feedback."""
    logger.info("Content ready for human review")

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
            requested_changes=[user_feedback],
            preserve_elements=[],
        )

    return {"human_feedback": feedback}
