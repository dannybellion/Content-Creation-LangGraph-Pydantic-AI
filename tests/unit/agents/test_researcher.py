import pytest

from src.agents.researcher import agent, conduct_research
from src.models.agent_outputs import ConsolidatedResearch

pytestmark = pytest.mark.anyio(backends=["asyncio"])


async def test_conduct_research_basic(
    sample_workflow_state, mock_web_search_researcher, test_model_override
):
    """Test basic research functionality."""
    with agent.agent.override(model=test_model_override):
        result = await conduct_research(sample_workflow_state)

    assert isinstance(result, ConsolidatedResearch)
    assert result.web_research
    assert isinstance(result.key_insights, list)
    assert isinstance(result.unique_angles, list)
    assert isinstance(result.expert_quotes, list)
    assert isinstance(result.statistics, list)
    assert isinstance(result.trending_topics, list)
    assert isinstance(result.content_gaps, list)
    assert result.research_quality_score >= 0.0
    assert result.research_quality_score <= 1.0


async def test_conduct_research_detailed_brief(
    mock_web_search_researcher, test_model_override
):
    """Test research with a detailed content brief."""
    from src.graph.state import WorkflowState
    from src.models.agent_outputs import ContentBrief

    detailed_state = WorkflowState(
        original_input="Comprehensive guide on AI automation tools",
        content_brief=ContentBrief(
            topic="AI Automation Tools for Enterprise",
            target_audience="CTOs and technical decision makers",
            content_type="comprehensive_guide",
            tone="authoritative",
            word_count_target=2500,
            key_points=[
                "implementation strategies",
                "ROI measurement",
                "security considerations",
                "scalability challenges",
            ],
            call_to_action="Schedule a consultation with our AI experts",
        ),
    )

    with agent.agent.override(model=test_model_override):
        result = await conduct_research(detailed_state)

    assert isinstance(result, ConsolidatedResearch)
    assert result.web_research
    assert len(result.key_insights) >= 0
    assert len(result.unique_angles) >= 0
    assert result.research_quality_score >= 0.0


async def test_conduct_research_technical_topic(
    mock_web_search_researcher, test_model_override
):
    """Test research on technical topics."""
    from src.graph.state import WorkflowState
    from src.models.agent_outputs import ContentBrief

    technical_state = WorkflowState(
        original_input="Machine learning model deployment",
        content_brief=ContentBrief(
            topic="MLOps and Model Deployment Best Practices",
            target_audience="data scientists and ML engineers",
            content_type="tutorial",
            tone="technical",
            word_count_target=1800,
            key_points=[
                "CI/CD for ML",
                "model versioning",
                "monitoring and observability",
                "rollback strategies",
            ],
            call_to_action="Try our ML deployment platform",
        ),
    )

    with agent.agent.override(model=test_model_override):
        result = await conduct_research(technical_state)

    assert isinstance(result, ConsolidatedResearch)
    assert result.web_research
    assert isinstance(result.key_insights, list)
    assert isinstance(result.trending_topics, list)


async def test_agent_structure():
    """Test that the agent is properly configured."""
    assert agent.name == "researcher"
    assert agent.output_type == ConsolidatedResearch
    assert len(agent.tools) == 1  # web_search tool
    assert agent.temperature == 0.1
