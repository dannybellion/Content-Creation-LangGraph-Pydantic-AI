"""
Shared pytest fixtures for all tests.
"""

import pytest
from unittest.mock import patch
from pydantic_ai import models
from pydantic_ai.models.test import TestModel

# Disable real model requests globally
models.ALLOW_MODEL_REQUESTS = False


@pytest.fixture
def mock_web_search():
    """Mock web_search tool to return predictable search results."""
    with patch("src.agents.content_writer.web_search") as mock:
        mock.return_value = """
        Mock search results for productivity tools:
        
        Title: "Top 10 AI Productivity Tools for 2024"
        URL: https://example.com/ai-tools
        Content: AI productivity tools are revolutionizing how we work. Studies show 40% increase in efficiency when using AI automation tools. Key benefits include time savings, reduced errors, and improved focus.
        
        Title: "How AI Tools Boost Workplace Productivity"  
        URL: https://example.com/productivity-boost
        Content: Companies using AI tools report 25% improvement in task completion rates. Popular tools include ChatGPT for writing, Notion AI for documentation, and Zapier for automation.
        
        Title: "AI Productivity Statistics 2024"
        URL: https://example.com/ai-stats
        Content: 75% of professionals use at least one AI tool daily. Average time savings: 2.5 hours per week. ROI typically seen within 3 months of implementation.
        """
        yield mock


@pytest.fixture
def mock_analyze_readability():
    """Mock analyze_readability tool to return predictable readability analysis."""
    with patch("src.agents.content_writer.analyze_readability") as mock:
        mock.return_value = str(
            {
                "flesch_score": 75.0,
                "grade_level": 8.0,
                "readability_level": "Standard",
                "target_audience": "8th-9th grade",
                "avg_sentence_length": 15.2,
                "total_words": 850,
                "total_sentences": 42,
                "recommendations": [
                    "Readability is good - maintain current writing style",
                    "Consider adding more transitional phrases for better flow",
                ],
            }
        )
        yield mock


@pytest.fixture
def mock_check_keyword_density():
    """Mock check_keyword_density tool to return predictable keyword analysis."""
    with patch("src.agents.content_writer.check_keyword_density") as mock:
        mock.return_value = str(
            {
                "total_words": 850,
                "keyword_analysis": {
                    "AI productivity": {
                        "exact_count": 8,
                        "density_percentage": 0.94,
                        "status": "optimal",
                        "recommendation": "Keyword density is well-optimized",
                        "word_counts": {"ai": 12, "productivity": 15},
                    },
                    "automation tools": {
                        "exact_count": 5,
                        "density_percentage": 0.59,
                        "status": "optimal",
                        "recommendation": "Keyword density is well-optimized",
                        "word_counts": {"automation": 8, "tools": 18},
                    },
                },
                "total_keyword_density": 1.53,
                "overall_assessment": "Well-optimized keyword usage",
            }
        )
        yield mock


@pytest.fixture
def mock_web_search_func():
    """Mock function for web_search tool."""

    async def mock_search(ctx, query: str) -> str:
        return """
        Mock search results for productivity tools:
        
        Title: "Top 10 AI Productivity Tools for 2024"
        URL: https://example.com/ai-tools
        Content: AI productivity tools are revolutionizing how we work. Studies show 40% increase in efficiency when using AI automation tools. Key benefits include time savings, reduced errors, and improved focus.
        """

    return mock_search


@pytest.fixture
def mock_readability_func():
    """Mock function for analyze_readability tool."""

    async def mock_analyze(ctx, content: str) -> str:
        return str(
            {
                "flesch_score": 75.0,
                "grade_level": 8.0,
                "readability_level": "Standard",
                "target_audience": "8th-9th grade",
                "avg_sentence_length": 15.2,
                "total_words": 850,
                "total_sentences": 42,
                "recommendations": [
                    "Readability is good - maintain current writing style",
                    "Consider adding more transitional phrases for better flow",
                ],
            }
        )

    return mock_analyze


@pytest.fixture
def mock_keyword_func():
    """Mock function for check_keyword_density tool."""

    async def mock_check(ctx, content: str, keywords: list[str]) -> str:
        return str(
            {
                "total_words": 850,
                "keyword_analysis": {
                    "AI productivity": {
                        "exact_count": 8,
                        "density_percentage": 0.94,
                        "status": "optimal",
                        "recommendation": "Keyword density is well-optimized",
                        "word_counts": {"ai": 12, "productivity": 15},
                    }
                },
                "total_keyword_density": 1.53,
                "overall_assessment": "Well-optimized keyword usage",
            }
        )

    return mock_check


@pytest.fixture
def mock_all_tools(
    mock_web_search, mock_analyze_readability, mock_check_keyword_density
):
    """Convenience fixture that applies all tool mocks."""
    yield {
        "web_search": mock_web_search,
        "analyze_readability": mock_analyze_readability,
        "check_keyword_density": mock_check_keyword_density,
    }


@pytest.fixture
def test_model_override():
    """Fixture to provide TestModel for agent overrides."""
    return TestModel(call_tools=[])


@pytest.fixture
def sample_workflow_state():
    """Create a sample workflow state for testing across all agents."""
    from src.models import (
        WorkflowState,
        ContentBrief,
        ContentPlan,
        ConsolidatedResearch,
    )

    return WorkflowState(
        original_input="Write about AI productivity tools",
        content_brief=ContentBrief(
            topic="AI Productivity Tools",
            target_audience="business professionals",
            content_type="blog_post",
            tone="professional",
            word_count_target=1000,
            key_points=["efficiency", "automation", "cost savings"],
            call_to_action="Try our AI tools today",
        ),
        content_plan=ContentPlan(
            title="10 AI Tools to Boost Your Productivity",
            hook="Transform your productivity with these game-changing AI tools",
            style="informative and actionable",
            key_ideas=[
                "AI tools save time and increase efficiency",
                "Implementation is easier than you think",
                "ROI is measurable and significant",
            ],
            content_differentiation="Focus on practical implementation rather than technical features",
            research_integration="Use real user testimonials and case studies throughout",
            audience_alignment="Written for busy professionals who want quick wins",
        ),
        consolidated_research=ConsolidatedResearch(
            web_research="AI tools market growing 25% annually",
            key_insights=[
                "AI adoption increasing rapidly",
                "Productivity gains measurable",
            ],
            unique_angles=["Focus on implementation", "Real user stories"],
            expert_quotes=["AI is transforming workplace efficiency"],
            statistics=["75% of users report improved productivity"],
            trending_topics=["automation", "AI integration"],
            content_gaps=["Need more real-world examples"],
            research_quality_score=0.8,
        ),
    )


@pytest.fixture
def sample_draft_content():
    """Create sample draft content for revision testing."""
    from src.models import DraftContent, ContentSection

    return DraftContent(
        title="Sample Content Title",
        hook_paragraph="Sample hook paragraph",
        sections=[
            ContentSection(
                heading="Introduction",
                content="Introduction content here",
            ),
            ContentSection(
                heading="Main Content",
                content="Main content section with detailed information",
            ),
        ],
        conclusion="Sample conclusion",
        meta_description="Sample meta description for SEO",
        tags=["productivity", "AI", "tools"],
        word_count=200,
        readability_score=75.0,
        call_to_action="Try these tips today!",
        author_notes="Sample content created for testing purposes",
    )


@pytest.fixture
def sample_human_feedback():
    """Create sample human feedback for revision testing."""
    from src.models import HumanFeedback

    return HumanFeedback(
        feedback_type="edit_content",
        comments="Make it more engaging and add more examples",
        requested_changes=[
            "Add more examples",
            "Improve introduction",
            "Enhance conclusion",
        ],
        priority="high",
        preserve_elements=["main structure", "key statistics"],
    )


@pytest.fixture
def mock_content_writer_agent(
    mock_web_search_func, mock_readability_func, mock_keyword_func
):
    """Create a content writer agent with mocked tools."""
    from src.agents.base import BaseAgent
    from src.models import DraftContent
    from src.prompts.prompt_manager import PromptManager

    return BaseAgent(
        name="content_writer",
        output_type=DraftContent,
        system_prompt=PromptManager.get_prompt("content_writer_system"),
        model_name="openai:gpt-4o-mini",
        temperature=0.1,
        tools=[mock_web_search_func, mock_readability_func, mock_keyword_func],
    )
