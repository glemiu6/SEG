"""Claim extraction with validated, quote-backed LLM output."""

from __future__ import annotations

from pydantic import BaseModel, Field

from evidence_graph.llm.client import OllamaClient
from evidence_graph.models.schema import Claim, Span


class ExtractedClaim(BaseModel):
    text: str = Field(min_length=1, max_length=1200)
    evidence_quote: str = Field(min_length=1, max_length=1600)
    conditions: list[str] = Field(default_factory=list, max_length=8)
    confidence: float = Field(ge=0.0, le=1.0)


class ClaimExtractionResult(BaseModel):
    claims: list[ExtractedClaim] = Field(default_factory=list, max_length=20)


class ClaimExtractor:
    """Extracts claims and drops outputs that cannot be traced to source text."""

    def __init__(self, client: OllamaClient):
        self.client = client

    def extract(self, paper_id: str, text: str, limit: int = 10) -> list[Claim]:
        prompt = f"""Extract at most {limit} check-worthy scientific claims from the paper text below.
Focus on findings, comparisons, and conclusions, not background or aspirations.
Each claim must be self-contained. evidence_quote must be an exact continuous quote from
the supplied text that grounds the claim. conditions should name material qualifiers such
as population, dataset, metric, method, or setting. Do not infer facts not in the text.

PAPER TEXT:
{text[:24000]}"""
        result = self.client.generate_structured(
            "You are a careful scientific claim extractor. Return only schema-valid JSON.",
            prompt,
            ClaimExtractionResult,
        )
        claims: list[Claim] = []
        for item in result.claims:
            start = text.find(item.evidence_quote)
            if start < 0:
                continue
            claims.append(Claim(
                id=f"{paper_id}:claim:{len(claims)}",
                paper_id=paper_id,
                text=item.text,
                source_span=Span(paper_id=paper_id, text=item.evidence_quote,
                                 char_start=start, char_end=start + len(item.evidence_quote)),
                conditions=item.conditions,
                confidence=item.confidence,
            ))
        return claims
