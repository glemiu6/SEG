"""Build a graph from extracted claims and classified evidence."""

from evidence_graph.graph.models import EvidenceGraph
from evidence_graph.models.schema import Claim
from evidence_graph.relations.classifier import EvidenceRelation


def build_evidence_graph(
    source_paper_id: str, claims: list[Claim], relations: list[EvidenceRelation]
) -> EvidenceGraph:
    return EvidenceGraph(source_paper_id=source_paper_id, claims=claims, relations=relations)
