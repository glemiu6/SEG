"""Evidence-graph serialization."""

from __future__ import annotations

from pathlib import Path

from evidence_graph.graph.models import EvidenceGraph


def export_json(graph: EvidenceGraph, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(graph.model_dump_json(indent=2), encoding="utf-8")
