"""
Pydantic models for the content creation pipeline.
"""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# Core Content Models
# ============================================================================


class ContentBrief(BaseModel):
    """Structured content brief parsed from free text input."""

    topic: str = Field(..., description="Main topic/subject of the content")
    target_audience: str = Field(..., description="Who this content is for")
    content_type: str = Field(..., description="Type of content")
    tone: str = Field(..., description="Tone of the content")
    word_count_target: int = Field(
        default=None, description="Target word count"
    )
    key_points: List[str] = Field(
        default_factory=list, description="Key points to cover"
    )
    call_to_action: Optional[str] = Field(
        None, description="Desired call to action"
    )


class BriefValidation(BaseModel):
    """Result of validating a content brief."""

    is_complete: bool = Field(
        ..., description="Whether the brief has sufficient information"
    )
    missing_fields: List[str] = Field(
        default_factory=list, description="Required fields that are missing"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Suggestions for improvement"
    )
    clarifying_questions: str = Field(
        ..., description="Message to ask the user for more information"
    )


class ContentIdea(BaseModel):
    """Individual content idea generated from research and brief."""

    title: str = Field(..., description="Short and clear title")
    hook: str = Field(
        ..., description="Scroll-stopping idea to pull people in"
    )
    angle: str = Field(
        ..., description="Unique point of view that makes this fresh"
    )
    description: str = Field(
        ..., description="Brief description of the content idea"
    )


class ContentIdeaOptions(BaseModel):
    """Collection of content idea options for user selection."""

    ideas: List[ContentIdea] = Field(
        ..., description="Generated content ideas", min_length=3, max_length=3
    )


class HeadlineVariation(BaseModel):
    """Individual headline variation with main points."""

    headline: str = Field(..., description="Compelling, specific headline")
    main_points: List[str] = Field(
        ...,
        description="3-5 main points that deliver on the headline promise",
        min_length=3,
        max_length=5,
    )
    hook_strength: int = Field(
        ..., ge=1, le=10, description="Hook strength rating 1-10"
    )
    target_audience_fit: int = Field(
        ..., ge=1, le=10, description="Audience alignment rating 1-10"
    )


class HeadlineOptions(BaseModel):
    """Collection of headline variations for strategic selection."""

    variations: List[HeadlineVariation] = Field(
        ...,
        description="Generated headline variations",
        min_length=15,
        max_length=20,
    )
    recommended_top_3: List[int] = Field(
        ...,
        description="Indices of top 3 recommended headlines",
        min_length=3,
        max_length=3,
    )


class ContentContainer(BaseModel):
    """Content framework/container for organizing the piece."""

    container_type: Literal[
        "rule_of_three",
        "listicle",
        "how_to_guide",
        "case_study",
        "framework",
        "story_based",
        "comparison",
        "trend_analysis",
    ] = Field(..., description="Type of content container/framework")
    magical_way: Literal[
        "tips",
        "stats",
        "steps",
        "lessons",
        "examples",
        "reasons",
        "stories",
        "quotes",
        "resources",
        "frameworks",
    ] = Field(..., description="The 'magical way' this content delivers value")
    structure_rationale: str = Field(
        ..., description="Why this container fits the content and audience"
    )
    sections_count: int = Field(
        ..., ge=3, le=10, description="Number of main sections"
    )


class Idea(BaseModel):
    """An idea for the content."""

    title: str = Field(..., description="Active title")
    background: str = Field(..., description="1000 words of background")


class PrioritizedIdea(BaseModel):
    """Prioritized content idea with strategic importance."""

    title: str = Field(..., description="Active, compelling section title")
    priority_rank: int = Field(
        ..., ge=1, le=3, description="Priority ranking (1=highest)"
    )
    value_proposition: str = Field(
        ..., description="Specific value this section delivers"
    )
    supporting_research: List[str] = Field(
        default_factory=list,
        description="Key research points supporting this idea",
    )


class ContentPlan(BaseModel):
    """Strategic content plan following Cole & Greg framework."""

    # Strategic headline decision
    selected_headline: str = Field(
        ..., description="Chosen headline that makes a clear promise"
    )
    headline_promise: str = Field(
        ..., description="What the headline promises to deliver"
    )

    # Container and structure
    content_container: ContentContainer = Field(
        ..., description="Selected content framework"
    )

    # Hook and opening strategy
    hook: str = Field(..., description="Scroll-stopping opening idea")
    opening_strategy: str = Field(
        ...,
        description="How to immediately capture attention and set expectations",
    )

    # Core content strategy
    key_ideas: List[PrioritizedIdea] = Field(
        ...,
        description="3 prioritized core messages (stack-ranked by impact)",
        min_length=3,
        max_length=3,
    )

    # Differentiation and positioning
    content_differentiation: str = Field(
        ..., description="Unique value proposition - what makes this different"
    )
    contrarian_angle: Optional[str] = Field(
        None,
        description="Counter-intuitive perspective that challenges assumptions",
    )

    # Research integration strategy
    research_integration: str = Field(
        ..., description="How to weave insights naturally into narrative"
    )
    surprising_insights: List[str] = Field(
        default_factory=list,
        description="Counter-intuitive findings to highlight",
    )
    actionable_takeaways: List[str] = Field(
        ...,
        description="Specific actions readers can take immediately",
        min_length=3,
    )

    # Audience and engagement
    audience_alignment: str = Field(
        ..., description="How content addresses audience pain points and goals"
    )
    funnel_strategy: str = Field(
        ...,
        description="How to lead with strongest material and maintain engagement",
    )

    # Quality assurance
    subhead_promise_check: bool = Field(
        ..., description="Confirmed that subheads deliver on headline promise"
    )
    tangible_value_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="How tangible/actionable the content is (1-10)",
    )
    content_style: str = Field(..., description="The style of the content")


# ============================================================================
# Research Models
# ============================================================================


class ConsolidatedResearch(BaseModel):
    """Merged research findings from all sources."""

    web_research: str = Field(..., description="Web research")
    youtube_research: str = Field(..., description="Youtube research")
    general_background: str = Field(..., description="General background")
    key_insights: List[str] = Field(..., description="Combined key insights")
    unique_angles: List[str] = Field(
        ..., description="Unique content angles discovered"
    )
    expert_quotes: List[str] = Field(
        default_factory=list, description="Quotable expert insights"
    )
    statistics: List[str] = Field(
        default_factory=list, description="Relevant statistics and data"
    )
    trending_topics: List[str] = Field(
        ..., description="Combined trending topics"
    )
    content_gaps: List[str] = Field(
        default_factory=list, description="Gaps in existing content"
    )
    research_quality_score: float = Field(
        ..., ge=0, le=1, description="Overall research quality"
    )


# ============================================================================
# Content Creation Models
# ============================================================================


class ContentSection(BaseModel):
    """Individual section of content."""

    heading: str = Field(..., description="Section heading")
    content: str = Field(..., description="Section content")


class DraftContent(BaseModel):
    """Final content output."""

    title: str = Field(..., description="Final title")
    hook_paragraph: str = Field(..., description="Hook paragraph")
    sections: List[ContentSection] = Field(..., description="The core ideas")
    conclusion: str = Field(..., description="Conclusion")
    meta_description: str = Field(..., description="SEO meta description")
    tags: List[str] = Field(..., description="Content tags")
    word_count: int = Field(..., description="Total word count")
    readability_score: float = Field(
        ..., ge=0, le=100, description="Readability score"
    )
    call_to_action: Optional[str] = Field(None, description="Call to action")
    author_notes: str = Field(..., description="Notes for the human reviewer")


# ============================================================================
# Workflow State Model
# ============================================================================


class HumanFeedback(BaseModel):
    """Human feedback on content."""

    feedback_type: Literal["approve", "edit_content", "change_plan"] = Field(
        ..., description="Type of feedback"
    )
    comments: str = Field(..., description="Specific feedback comments")
    requested_changes: List[str] = Field(
        default_factory=list, description="Specific changes requested"
    )
    priority: Literal["high", "medium", "low"] = "medium"
    preserve_elements: List[str] = Field(
        default_factory=list, description="Elements to keep unchanged"
    )


class WorkflowState(BaseModel):
    """Complete state of the content creation workflow."""

    # Input
    original_input: str = Field(..., description="Original free text input")

    # Parsed and validated brief
    content_brief: Optional[ContentBrief] = None
    brief_validation: Optional[BriefValidation] = None

    # Research
    web_research: Optional[str] = None
    # youtube_research: Optional[YouTubeResearchResults] = None
    consolidated_research: Optional[ConsolidatedResearch] = None

    # Content ideas and headlines
    content_idea_options: Optional[ContentIdeaOptions] = None
    selected_content_idea: Optional[ContentIdea] = None
    headline_options: Optional[HeadlineOptions] = None
    selected_headline_variation: Optional[HeadlineVariation] = None

    # Planning
    content_plan: Optional[ContentPlan] = None

    # Content creation
    draft_content: Optional[DraftContent] = None

    # Human review
    human_feedback: Optional[HumanFeedback] = None

    # User interaction
    user_response: Optional[str] = None

    # Workflow metadata
    current_step: str = "parse_brief"
    revision_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_complete: bool = False

    def update_step(self, step: str):
        """Update the current workflow step."""
        self.current_step = step
        self.updated_at = datetime.now()

    def increment_revision(self):
        """Increment revision counter."""
        self.revision_count += 1
        self.updated_at = datetime.now()


# ============================================================================
# Configuration Models
# ============================================================================


class AgentConfig(BaseModel):
    """Configuration for individual agents."""

    model_name: str = "gpt-4o"
    temperature: float = 0.0
    max_retries: int = 3
    timeout_seconds: int = 60


class WorkflowConfig(BaseModel):
    """Configuration for the entire workflow."""

    max_revisions: int = 3
    max_research_results: int = 10
    target_research_quality: float = 0.8
    enable_youtube_research: bool = True
    enable_web_research: bool = True
    content_writer_config: AgentConfig = Field(default_factory=AgentConfig)
    planner_config: AgentConfig = Field(default_factory=AgentConfig)
    researcher_config: AgentConfig = Field(default_factory=AgentConfig)
