"""
Pydantic models for the content creation pipeline.
"""

from datetime import datetime
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Core Content Models
# ============================================================================

class ContentBrief(BaseModel):
    """Structured content brief parsed from free text input."""
    topic: str = Field(..., description="Main topic/subject of the content")
    target_audience: str = Field(..., description="Who this content is for")
    content_type: Literal["blog_post", "article", "social_media", "email", "landing_page"] = "blog_post"
    tone: Literal["professional", "casual", "technical", "friendly", "authoritative"] = "professional"
    word_count_target: int = Field(default=800, description="Target word count")
    key_points: List[str] = Field(default_factory=list, description="Key points to cover")
    seo_keywords: List[str] = Field(default_factory=list, description="Primary SEO keywords")
    call_to_action: Optional[str] = Field(None, description="Desired call to action")
    brand_guidelines: Optional[str] = Field(None, description="Brand voice and style requirements")
    deadline: Optional[datetime] = Field(None, description="Content deadline")


class ValidationQuestion(BaseModel):
    """Question for clarifying incomplete content briefs."""
    question: str = Field(..., description="The clarifying question")
    field: str = Field(..., description="Which field this question relates to")
    required: bool = Field(default=True, description="Whether this is required or optional")


class BriefValidation(BaseModel):
    """Result of validating a content brief."""
    is_complete: bool = Field(..., description="Whether the brief has sufficient information")
    missing_fields: List[str] = Field(default_factory=list, description="Required fields that are missing")
    clarifying_questions: List[ValidationQuestion] = Field(default_factory=list, description="Questions to ask the user")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in brief completeness")


class ContentPlan(BaseModel):
    """Detailed plan for content creation."""
    title: str = Field(..., description="Proposed title for the content")
    subtitle: Optional[str] = Field(None, description="Optional subtitle")
    outline: List[str] = Field(..., description="Section headings and structure")
    key_messages: List[str] = Field(..., description="Core messages to communicate")
    target_keywords: List[str] = Field(..., description="Keywords to target for SEO")
    estimated_word_count: int = Field(..., description="Estimated final word count")
    research_angles: List[str] = Field(..., description="Angles to research")
    unique_value_proposition: str = Field(..., description="What makes this content unique")


# ============================================================================
# Research Models
# ============================================================================

class WebResult(BaseModel):
    """Individual web search result."""
    title: str = Field(..., description="Title of the web page")
    url: str = Field(..., description="URL of the source")
    snippet: str = Field(..., description="Brief description/snippet")
    content: Optional[str] = Field(None, description="Extracted content if available")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance to the query")
    publish_date: Optional[datetime] = Field(None, description="Publication date if available")


class WebResearchResults(BaseModel):
    """Results from web research."""
    query: str = Field(..., description="Search query used")
    results: List[WebResult] = Field(..., description="Search results")
    key_insights: List[str] = Field(..., description="Key insights extracted")
    trending_topics: List[str] = Field(..., description="Trending topics discovered")
    statistics: List[str] = Field(default_factory=list, description="Relevant statistics found")
    total_results: int = Field(..., description="Total number of results found")


class YouTubeVideo(BaseModel):
    """Individual YouTube video result."""
    title: str = Field(..., description="Video title")
    video_id: str = Field(..., description="YouTube video ID")
    url: str = Field(..., description="Full YouTube URL")
    description: str = Field(..., description="Video description")
    view_count: Optional[int] = Field(None, description="Number of views")
    duration: Optional[str] = Field(None, description="Video duration")
    upload_date: Optional[datetime] = Field(None, description="Upload date")
    channel_name: str = Field(..., description="Channel name")
    transcript: Optional[str] = Field(None, description="Video transcript if available")
    key_points: List[str] = Field(default_factory=list, description="Key points from the video")


class YouTubeResearchResults(BaseModel):
    """Results from YouTube research."""
    query: str = Field(..., description="Search query used")
    videos: List[YouTubeVideo] = Field(..., description="Video results")
    key_insights: List[str] = Field(..., description="Key insights from videos")
    trending_topics: List[str] = Field(..., description="Trending topics from videos")
    expert_opinions: List[str] = Field(default_factory=list, description="Expert opinions found")
    total_videos: int = Field(..., description="Total number of videos found")


class ConsolidatedResearch(BaseModel):
    """Merged research findings from all sources."""
    web_research: WebResearchResults
    youtube_research: YouTubeResearchResults
    key_insights: List[str] = Field(..., description="Combined key insights")
    unique_angles: List[str] = Field(..., description="Unique content angles discovered")
    expert_quotes: List[str] = Field(default_factory=list, description="Quotable expert insights")
    statistics: List[str] = Field(default_factory=list, description="Relevant statistics and data")
    trending_topics: List[str] = Field(..., description="Combined trending topics")
    content_gaps: List[str] = Field(default_factory=list, description="Gaps in existing content")
    research_quality_score: float = Field(..., ge=0, le=1, description="Overall research quality")


# ============================================================================
# Content Creation Models
# ============================================================================

class ContentSection(BaseModel):
    """Individual section of content."""
    heading: str = Field(..., description="Section heading")
    content: str = Field(..., description="Section content")
    word_count: int = Field(..., description="Word count for this section")
    key_points: List[str] = Field(default_factory=list, description="Key points covered")


class SEOAnalysis(BaseModel):
    """SEO analysis of the content."""
    title_optimization: float = Field(..., ge=0, le=1, description="Title SEO score")
    keyword_density: Dict[str, float] = Field(..., description="Keyword density analysis")
    readability_score: float = Field(..., ge=0, le=100, description="Content readability score")
    meta_description: str = Field(..., description="Suggested meta description")
    internal_links: List[str] = Field(default_factory=list, description="Suggested internal links")
    overall_seo_score: float = Field(..., ge=0, le=100, description="Overall SEO score")


class DraftContent(BaseModel):
    """Final content output."""
    title: str = Field(..., description="Final title")
    content: str = Field(..., description="Full content body")
    sections: List[ContentSection] = Field(..., description="Structured content sections")
    meta_description: str = Field(..., description="SEO meta description")
    tags: List[str] = Field(..., description="Content tags")
    word_count: int = Field(..., description="Total word count")
    readability_score: float = Field(..., ge=0, le=100, description="Readability score")
    seo_analysis: SEOAnalysis = Field(..., description="SEO analysis")
    call_to_action: Optional[str] = Field(None, description="Call to action")
    author_notes: str = Field(..., description="Notes for the human reviewer")
    estimated_read_time: int = Field(..., description="Estimated reading time in minutes")


# ============================================================================
# Workflow State Model
# ============================================================================

class HumanFeedback(BaseModel):
    """Human feedback on content."""
    feedback_type: Literal["approve", "edit_content", "change_plan"] = Field(..., description="Type of feedback")
    comments: str = Field(..., description="Specific feedback comments")
    requested_changes: List[str] = Field(default_factory=list, description="Specific changes requested")
    priority: Literal["high", "medium", "low"] = "medium"
    preserve_elements: List[str] = Field(default_factory=list, description="Elements to keep unchanged")


class WorkflowState(BaseModel):
    """Complete state of the content creation workflow."""
    # Input
    original_input: str = Field(..., description="Original free text input")
    
    # Parsed and validated brief
    content_brief: Optional[ContentBrief] = None
    brief_validation: Optional[BriefValidation] = None
    
    # Planning
    content_plan: Optional[ContentPlan] = None
    
    # Research
    web_research: Optional[WebResearchResults] = None
    youtube_research: Optional[YouTubeResearchResults] = None
    consolidated_research: Optional[ConsolidatedResearch] = None
    
    # Content creation
    draft_content: Optional[DraftContent] = None
    
    # Human review
    human_feedback: Optional[HumanFeedback] = None
    
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