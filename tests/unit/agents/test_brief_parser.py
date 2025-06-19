import pytest

from src.agents.brief_parser import agent, parse_brief
from src.models import ContentBrief

pytestmark = pytest.mark.anyio(backends=["asyncio"])


async def test_parse_brief_basic(test_model_override):
    """Test basic brief parsing functionality."""
    input_text = "Write a blog post about AI productivity tools for business professionals"

    with agent.agent.override(model=test_model_override):
        result = await parse_brief(input_text)

    assert isinstance(result, ContentBrief)
    assert result.topic
    assert result.target_audience
    assert result.content_type
    assert result.tone
    assert result.word_count_target is None or result.word_count_target > 0
    assert isinstance(result.key_points, list)


async def test_parse_brief_detailed_input(test_model_override):
    """Test parsing with detailed input text."""
    input_text = """
    I need a comprehensive guide about remote work productivity tools. 
    Target audience: remote workers and managers.
    Word count: around 1500 words.
    Tone: professional but friendly.
    Key focus areas: communication tools, task management, time tracking.
    Call to action: Sign up for our productivity newsletter.
    """

    with agent.agent.override(model=test_model_override):
        result = await parse_brief(input_text)

    assert isinstance(result, ContentBrief)
    assert result.topic
    assert result.target_audience
    assert result.content_type
    assert result.tone
    assert result.word_count_target is None or result.word_count_target > 0
    assert isinstance(result.key_points, list)
    # call_to_action is optional, just check it exists as an attribute
    assert hasattr(result, "call_to_action")


async def test_parse_brief_minimal_input(test_model_override):
    """Test parsing with minimal input."""
    input_text = "Write about social media marketing"

    with agent.agent.override(model=test_model_override):
        result = await parse_brief(input_text)

    assert isinstance(result, ContentBrief)
    assert result.topic
    assert result.target_audience  # Should have default values
    assert result.content_type
    assert result.tone
    assert result.word_count_target is None or result.word_count_target > 0


async def test_agent_structure():
    """Test that the agent is properly configured."""
    assert agent.name == "brief_parser"
    assert agent.output_type == ContentBrief
    assert agent.tools == []  # No tools for brief parser
    assert agent.temperature == 0.1
