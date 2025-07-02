"""
Simple domain models for the content creation pipeline.
"""

from pydantic import BaseModel, Field


class Idea(BaseModel):
    """An idea for the content."""

    title: str = Field(..., description="Active title")
    background: str = Field(..., description="1000 words of background")
