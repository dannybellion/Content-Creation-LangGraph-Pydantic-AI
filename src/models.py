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
    
    
class Idea(BaseModel):
    """An idea for the content."""
    
    title: str = Field(..., description="Active title")
    background: str = Field(..., description="1000 words of background")


class ContentPlan(BaseModel):
    """Detailed plan for content creation."""

    title: str = Field(..., description="Proposed title for the content")
    hook: str = Field(..., description="Scroll-stopping idea")
    style: str = Field(..., description="Style of the content")
    key_ideas: List[Idea] = Field(
        ..., description="3 Core messages"
    )
    content_differentiation: str = Field(
        ..., description="What makes this content different"
    )
    research_integration: str = Field(
        ..., description="How to integrate research into the content"
    )
    audience_alignment: str = Field(
        ..., description="How to align the content to the audience"
    )


# ============================================================================
# Research Models
# ============================================================================


class ConsolidatedResearch(BaseModel):
    """Merged research findings from all sources."""

    web_research: str = Field(..., description="Web research")
    youtube_research: str = Field(..., description="Youtube research")
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
    sections: List[ContentSection] = Field(
        ..., description="The core ideas"
    )
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

    # Content ideas
    content_idea_options: Optional[ContentIdeaOptions] = None
    selected_content_idea: Optional[ContentIdea] = None

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
