"""
Workflow state definition for the content creation pipeline.
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

from src.models.agent_outputs import (
    ContentBrief,
    BriefValidation,
    ConsolidatedResearch,
    ContentIdeaOptions,
    ContentIdea,
    HeadlineOptions,
    HeadlineVariation,
    ContentPlan,
    DraftContent,
)


class HumanFeedback(BaseModel):
    """Human feedback on content."""

    feedback_type: Literal["approve", "edit_content", "change_plan"] = Field(
        ..., description="Type of feedback"
    )
    comments: str = Field(..., description="Specific feedback comments")
    requested_changes: list[str] = Field(
        default_factory=list, description="Specific changes requested"
    )
    priority: Literal["high", "medium", "low"] = "medium"
    preserve_elements: list[str] = Field(
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
