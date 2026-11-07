"""Validated structured output produced by a local language model."""

from pydantic import BaseModel, Field


class PaperAnalysis(BaseModel):
    summary: str = Field(min_length=1, max_length=1200)
    research_areas: list[str] = Field(min_length=1, max_length=6)
    relevance: str = Field(min_length=1, max_length=1200)
