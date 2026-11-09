from evidence_graph.models.schema import Span
from evidence_graph.retrieval.evidence_search import EvidenceSearcher


def test_evidence_search_returns_relevant_passage_first():
    searcher = EvidenceSearcher([
        Span(paper_id="a", text="We measure a substantial improvement in retrieval recall."),
        Span(paper_id="b", text="The microscope was calibrated before imaging."),
    ])

    results = searcher.search("retrieval recall improves", limit=1)

    assert results[0].paper_id == "a"


def test_evidence_search_returns_no_match_for_unrelated_query():
    searcher = EvidenceSearcher([Span(paper_id="a", text="A calibrated imaging microscope.")])
    assert searcher.search("language model alignment") == []
