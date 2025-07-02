import pytest

from src.agents.headline_generator import agent, generate_headlines
from src.models.agent_outputs import HeadlineOptions

pytestmark = pytest.mark.anyio(backends=["asyncio"])


async def test_generate_headlines_basic(
    sample_workflow_state, test_model_override
):
    """Test basic headline generation functionality."""
    with agent.agent.override(model=test_model_override):
        result = await generate_headlines(sample_workflow_state)

    assert isinstance(result, HeadlineOptions)
    assert isinstance(result.variations, list)
    assert len(result.variations) > 0

    # Check each variation has required fields
    for variation in result.variations:
        assert variation.headline
        assert variation.main_points
        assert variation.hook_strength
        assert variation.target_audience_fit
        assert len(variation.headline) > 0
        assert len(variation.main_points) >= 3
        assert 1 <= variation.hook_strength <= 10
        assert 1 <= variation.target_audience_fit <= 10


async def test_generate_headlines_different_content_types(
    mock_web_search_researcher, test_model_override
):
    """Test headline generation for different content types."""
    from src.graph.state import WorkflowState
    from src.models.agent_outputs import ContentBrief, ConsolidatedResearch

    # Test with different content types
    content_types = ["blog_post", "guide", "tutorial", "case_study"]

    for content_type in content_types:
        state = WorkflowState(
            original_input=f"Write a {content_type} about AI tools",
            content_brief=ContentBrief(
                topic="AI Productivity Tools",
                target_audience="business professionals",
                content_type=content_type,
                tone="professional",
                word_count_target=1000,
                key_points=["efficiency", "automation"],
                call_to_action="Try our tools",
            ),
            consolidated_research=ConsolidatedResearch(
                web_research="AI tools market analysis",
                youtube_research="Video content on AI tools",
                general_background="General AI tools background",
                key_insights=["Growing adoption", "Measurable ROI"],
                unique_angles=["Focus on SMBs"],
                expert_quotes=["AI is transforming work"],
                statistics=["40% productivity increase"],
                trending_topics=["automation"],
                content_gaps=["Real examples needed"],
                research_quality_score=0.8,
            ),
        )

        with agent.agent.override(model=test_model_override):
            result = await generate_headlines(state)

        assert isinstance(result, HeadlineOptions)
        assert len(result.variations) > 0


async def test_generate_headlines_different_audiences(test_model_override):
    """Test headline generation for different target audiences."""
    from src.graph.state import WorkflowState
    from src.models.agent_outputs import ContentBrief, ConsolidatedResearch

    audiences = [
        "business executives",
        "small business owners",
        "technical professionals",
        "marketing teams",
    ]

    for audience in audiences:
        state = WorkflowState(
            original_input=f"Content for {audience}",
            content_brief=ContentBrief(
                topic="Digital Marketing Automation",
                target_audience=audience,
                content_type="guide",
                tone="professional",
                word_count_target=1200,
                key_points=["efficiency", "ROI"],
                call_to_action="Get started today",
            ),
            consolidated_research=ConsolidatedResearch(
                web_research="Marketing automation trends",
                youtube_research="Video content on marketing automation",
                general_background="General marketing automation background",
                key_insights=["Automation saves time"],
                unique_angles=["Focus on ease of use"],
                expert_quotes=["Automation is key to scaling"],
                statistics=["60% time savings reported"],
                trending_topics=["AI integration"],
                content_gaps=["Need practical examples"],
                research_quality_score=0.7,
            ),
        )

        with agent.agent.override(model=test_model_override):
            result = await generate_headlines(state)

        assert isinstance(result, HeadlineOptions)
        assert len(result.variations) > 0


async def test_generate_headlines_different_tones(test_model_override):
    """Test headline generation with different tones."""
    from src.graph.state import WorkflowState
    from src.models.agent_outputs import ContentBrief, ConsolidatedResearch

    tones = ["professional", "casual", "authoritative", "friendly"]

    for tone in tones:
        state = WorkflowState(
            original_input=f"Content with {tone} tone",
            content_brief=ContentBrief(
                topic="Remote Work Productivity",
                target_audience="remote workers",
                content_type="blog_post",
                tone=tone,
                word_count_target=800,
                key_points=["focus", "communication"],
                call_to_action="Join our community",
            ),
            consolidated_research=ConsolidatedResearch(
                web_research="Remote work statistics",
                youtube_research="Video content on remote work",
                general_background="General remote work background",
                key_insights=["Flexibility increases satisfaction"],
                unique_angles=["Focus on work-life balance"],
                expert_quotes=["Remote work is here to stay"],
                statistics=["85% prefer remote work"],
                trending_topics=["hybrid work models"],
                content_gaps=["Practical tips needed"],
                research_quality_score=0.85,
            ),
        )

        with agent.agent.override(model=test_model_override):
            result = await generate_headlines(state)

        assert isinstance(result, HeadlineOptions)
        assert len(result.variations) > 0


async def test_agent_structure():
    """Test that the agent is properly configured."""
    assert agent.name == "headline_generator"
    assert agent.output_type == HeadlineOptions
    assert agent.tools == []  # No tools for headline generator
    assert agent.temperature == 0.2  # Higher temperature for creativity
