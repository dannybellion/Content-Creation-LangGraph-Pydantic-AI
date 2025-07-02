import pytest

from src.agents.brief_validator import agent, validate_brief
from src.models.agent_outputs import BriefValidation, ContentBrief

pytestmark = pytest.mark.anyio(backends=["asyncio"])


async def test_validate_brief_complete(
    sample_workflow_state, test_model_override
):
    """Test validation of a complete brief."""
    brief = sample_workflow_state.content_brief

    with agent.agent.override(model=test_model_override):
        result = await validate_brief(brief)

    assert isinstance(result, BriefValidation)
    assert isinstance(result.is_complete, bool)
    assert isinstance(result.missing_fields, list)
    assert isinstance(result.suggestions, list)
    assert isinstance(result.clarifying_questions, str)


async def test_validate_brief_incomplete(test_model_override):
    """Test validation of an incomplete brief."""
    brief = ContentBrief(
        topic="AI tools",
        target_audience="",  # Missing
        content_type="blog_post",
        tone="",  # Missing
        word_count_target=0,  # Invalid
        key_points=[],  # Empty
        call_to_action="",  # Missing
    )

    with agent.agent.override(model=test_model_override):
        result = await validate_brief(brief)

    assert isinstance(result, BriefValidation)
    assert isinstance(result.is_complete, bool)
    assert isinstance(result.missing_fields, list)
    assert isinstance(result.suggestions, list)
    assert isinstance(result.clarifying_questions, str)


async def test_validate_brief_minimal_valid(test_model_override):
    """Test validation of a minimal but valid brief."""
    brief = ContentBrief(
        topic="Social Media Marketing Best Practices",
        target_audience="small business owners",
        content_type="guide",
        tone="professional",
        word_count_target=800,
        key_points=["engagement", "content strategy"],
        call_to_action="Contact us for consultation",
    )

    with agent.agent.override(model=test_model_override):
        result = await validate_brief(brief)

    assert isinstance(result, BriefValidation)
    assert isinstance(result.is_complete, bool)
    assert isinstance(result.missing_fields, list)
    assert isinstance(result.suggestions, list)
    assert isinstance(result.clarifying_questions, str)


async def test_agent_structure():
    """Test that the agent is properly configured."""
    assert agent.name == "brief_validator"
    assert agent.output_type == BriefValidation
    assert agent.tools == []  # No tools for brief validator
    assert agent.temperature == 0.1
