"""Portable evidence-graph output models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from evidence_graph.models.schema import Claim
from evidence_graph.relations.classifier import EvidenceRelation


class EvidenceGraph(BaseModel):
    source_paper_id: str
    claims: list[Claim] = Field(default_factory=list)
    relations: list[EvidenceRelation] = Field(default_factory=list)
