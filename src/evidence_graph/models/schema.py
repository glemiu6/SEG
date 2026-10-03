from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, model_validator


SCHEMA_VERSION = "0.1.0"


class Span(BaseModel):
    paper_id: str
    section_id: str | None = None
    paragraph_id: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    char_start: int | None = None   # offsets inside the paragraph's text
    char_end: int | None = None
    text: str = Field(min_length=1)  # the exact quoted text

    @model_validator(mode="after")
    def _check_offsets(self) -> "Span":
        if (self.char_start is None) != (self.char_end is None):
            raise ValueError("char_start and char_end must be set together")
        if self.char_start is not None:
            if self.char_start < 0 or self.char_end <= self.char_start:
                raise ValueError("require 0 <= char_start < char_end")
            if self.char_end - self.char_start != len(self.text):
                raise ValueError("text length does not match offsets")
        return self


class SectionType(str, Enum):
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    RELATED_WORK = "related_work"
    METHOD = "method"
    EXPERIMENTS = "experiments"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    LIMITATIONS = "limitations"
    OTHER = "other"


class CitationMention(BaseModel):
    marker: str
    char_start:int
    char_end:int
    cited_paper_id: str | None = None


class Paragraph(BaseModel):
    id:str
    section_id:str
    text:str
    page_start: int | None = None
    page_end: int | None = None
    citations: list[CitationMention] = Field(default_factory=list)


class Section(BaseModel):
    id:str
    heading:str
    type: SectionType = Field(default=SectionType.OTHER)
    paragraphs: list[Paragraph] = Field(default_factory=list)

class Paper(BaseModel):
    id: str
    title: str
    doi: str | None = None
    year: int | None = None
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None
    sections: list[Section] = Field(default_factory=list)
    parse_source: str                # which parser produced this
    schema_version: str = SCHEMA_VERSION