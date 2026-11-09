"""Evidence-level stance classification."""

from __future__ import annotations

from pydantic import BaseModel, Field

from evidence_graph.llm.client import OllamaClient
from evidence_graph.models.schema import Claim, Span, Stance


class StanceResult(BaseModel):
    stance: Stance
    rationale: str = Field(min_length=1, max_length=1000)
    confidence: float = Field(ge=0.0, le=1.0)


class EvidenceRelation(BaseModel):
    claim_id: str
    evidence_span: Span
    stance: Stance
    rationale: str
    confidence: float


class StanceClassifier:
    def __init__(self, client: OllamaClient):
        self.client = client

    def classify(self, claim: Claim, evidence: Span) -> EvidenceRelation:
        prompt = f"""Compare the scientific claim and evidence passage below. Classify only their
relationship: supports, contradicts, qualifies, neutral, or not_relevant. A different
dataset, population, metric, method, or setting is not automatically a contradiction;
use qualifies when those conditions limit an otherwise related finding. Use only supplied text.

CLAIM: {claim.text}
CLAIM CONDITIONS: {', '.join(claim.conditions) or 'none stated'}
EVIDENCE PASSAGE: {evidence.text}"""
        result = self.client.generate_structured(
            "You are a conservative scientific evidence reviewer. Return only schema-valid JSON.",
            prompt,
            StanceResult,
        )
        return EvidenceRelation(claim_id=claim.id, evidence_span=evidence, stance=result.stance,
                                rationale=result.rationale, confidence=result.confidence)
