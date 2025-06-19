import pytest
from unittest.mock import patch

from src.agents.content_editor import agent, make_editorial_decisions
from src.models import ContentPlan, HeadlineVariation

pytestmark = pytest.mark.anyio(backends=["asyncio"])


@pytest.fixture
def mock_style_guidelines():
    """Mock style_guidelines tool to return predictable guidelines."""
    with patch("src.agents.content_editor.style_guidelines") as mock:

        async def mock_guidelines(ctx, content_type: str) -> str:
            return f"""
            Style Guidelines for {content_type}:
            
            1. Keep paragraphs short and scannable
            2. Use active voice and strong verbs
            3. Include compelling statistics and data
            4. End with clear call-to-action
            5. Optimize for engagement metrics
            """

        mock.side_effect = mock_guidelines
        yield mock


async def test_make_editorial_decisions_basic(
    sample_workflow_state, mock_style_guidelines, test_model_override
):
    """Test basic editorial decision making functionality."""
    # Add a selected headline variation to the state
    sample_workflow_state.selected_headline_variation = HeadlineVariation(
        headline="Transform Your Productivity with AI",
        main_points=[
            "Choose the right tools",
            "Implement systematically",
            "Measure results",
        ],
        hook_strength=8,
        target_audience_fit=9,
    )

    with agent.agent.override(model=test_model_override):
        result = await make_editorial_decisions(sample_workflow_state)

    assert isinstance(result, ContentPlan)
    # Test the fields that actually exist in ContentPlan
    assert hasattr(result, "selected_headline")
    assert hasattr(result, "hook")
    assert hasattr(result, "content_style")
    assert hasattr(result, "key_ideas")
    assert hasattr(result, "content_differentiation")
    assert hasattr(result, "research_integration")
    assert hasattr(result, "audience_alignment")


async def test_make_editorial_decisions_without_headline(
    sample_workflow_state, mock_style_guidelines, test_model_override
):
    """Test editorial decisions when no headline variation is selected."""
    # Ensure no selected headline variation
    sample_workflow_state.selected_headline_variation = None

    with agent.agent.override(model=test_model_override):
        result = await make_editorial_decisions(sample_workflow_state)

    assert isinstance(result, ContentPlan)
    assert hasattr(result, "selected_headline")
    assert hasattr(result, "hook")
    assert hasattr(result, "content_style")
    assert hasattr(result, "key_ideas")


async def test_make_editorial_decisions_with_rich_research(
    sample_workflow_state, mock_style_guidelines, test_model_override
):
    """Test editorial decisions with comprehensive research data."""
    # Enhance research data
    sample_workflow_state.consolidated_research.expert_quotes = [
        "AI is revolutionizing workplace productivity - Dr. Smith, Tech Research Institute",
        "We've seen 40% efficiency gains with AI implementation - Jane Doe, CEO",
    ]
    sample_workflow_state.consolidated_research.statistics = [
        "75% of professionals report improved productivity with AI tools",
        "Average time savings: 2.5 hours per week per employee",
    ]

    with agent.agent.override(model=test_model_override):
        result = await make_editorial_decisions(sample_workflow_state)

    assert isinstance(result, ContentPlan)
    assert hasattr(result, "selected_headline")
    assert hasattr(result, "research_integration")


async def test_agent_structure(mock_style_guidelines):
    """Test that the agent is properly configured."""
    assert agent.name == "content_editor"
    assert agent.output_type == ContentPlan
    assert len(agent.tools) == 1  # style_guidelines tool
    assert agent.temperature == 0.1
