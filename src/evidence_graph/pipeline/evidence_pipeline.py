"""End-to-end evidence-graph vertical slice."""

from __future__ import annotations

import re
from pathlib import Path

from evidence_graph.extraction.claims import ClaimExtractor
from evidence_graph.graph.builder import build_evidence_graph
from evidence_graph.graph.models import EvidenceGraph
from evidence_graph.ingestion.paragraph_parser import ParagraphParser
from evidence_graph.ingestion.pdf_reader import PDFReader
from evidence_graph.llm.client import OllamaClient
from evidence_graph.models.schema import Span
from evidence_graph.relations.classifier import StanceClassifier
from evidence_graph.retrieval.evidence_search import EvidenceSearcher


def _paper_id(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-") or "paper"


def corpus_passages(corpus_dir: Path, excluded: Path) -> list[Span]:
    """Load quoteable passages from PDFs directly under a small local corpus directory."""
    if not corpus_dir.is_dir():
        raise ValueError("--evidence-corpus must be a directory containing text-based PDFs")
    parser = ParagraphParser()
    passages: list[Span] = []
    excluded = excluded.resolve()
    for path in sorted(corpus_dir.glob("*.pdf")):
        if path.resolve() == excluded:
            continue
        paper_id = _paper_id(path)
        text = PDFReader(path).extract().text
        for paragraph in parser.parse(text, paper_id):
            # Very short fragments rarely contain interpretable scientific evidence.
            if len(paragraph.text) >= 100:
                passages.append(Span(paper_id=paper_id, paragraph_id=paragraph.id, text=paragraph.text))
    return passages


def build_from_pdf(
    paper_path: Path,
    corpus_dir: Path,
    client: OllamaClient,
    max_claims: int = 10,
    passages_per_claim: int = 5,
) -> EvidenceGraph:
    source = PDFReader(paper_path).extract()
    source_id = _paper_id(paper_path)
    claims = ClaimExtractor(client).extract(source_id, source.text, max_claims)
    searcher = EvidenceSearcher(corpus_passages(corpus_dir, paper_path))
    classifier = StanceClassifier(client)
    relations = []
    for claim in claims:
        for evidence in searcher.search(claim.text, passages_per_claim):
            relation = classifier.classify(claim, evidence)
            if relation.stance.value not in {"not_relevant", "neutral"}:
                relations.append(relation)
    return build_evidence_graph(source_id, claims, relations)
