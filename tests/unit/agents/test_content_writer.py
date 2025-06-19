import pytest

from src.agents.content_writer import agent, write_content, revise_content
from src.models import (
    DraftContent,
)

pytestmark = pytest.mark.anyio(backends=["asyncio"])


async def test_write_content_basic(sample_workflow_state, test_model_override):
    """Test basic content writing functionality."""

    with agent.agent.override(model=test_model_override):
        result = await write_content(sample_workflow_state)

    assert isinstance(result, DraftContent)
    assert result.title
    assert result.sections
    assert result.word_count >= 0
    assert result.readability_score >= 0
    assert result.readability_score <= 100
    assert isinstance(result.sections, list)
    assert result.meta_description
    assert isinstance(result.tags, list)


async def test_revise_content_with_feedback(
    sample_workflow_state,
    sample_draft_content,
    sample_human_feedback,
    test_model_override,
):
    """Test content revision with human feedback."""
    sample_workflow_state.draft_content = sample_draft_content
    sample_workflow_state.human_feedback = sample_human_feedback

    with agent.agent.override(model=test_model_override):
        result = await revise_content(sample_workflow_state)

    assert isinstance(result, DraftContent)
    assert result.title
    assert result.sections
    assert result.author_notes


async def test_agent_structure():
    """Test that the agent is properly configured."""
    assert agent.name == "content_writer"
    assert agent.output_type == DraftContent
    assert (
        len(agent.tools) == 3
    )
