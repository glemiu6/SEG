from evidence_graph.main import _format_authors, _print_results
from evidence_graph.retrieval.paper_search import RecommendedPaper


def test_format_authors_limits_long_lists():
    assert _format_authors(("One", "Two", "Three", "Four")) == "One, Two, Three et al."
    assert _format_authors(()) == "Unknown authors"


def test_readable_output_contains_labeled_fields(capsys, monkeypatch):
    monkeypatch.setattr("evidence_graph.main._terminal_width", lambda: 80)
    paper = RecommendedPaper(
        title="A useful paper", authors=("Ada Author",), year=2025,
        venue="Example Conference", url="https://example.test", doi=None,
        abstract="This paper presents a useful method.", areas=("Retrieval",),
        citation_count=1, score=1.0, semantic_score=0.91,
    )
    _print_results("Source paper", "retrieval method", [paper], [None])
    output = capsys.readouterr().out
    assert "SEG · PAPER RECOMMENDATIONS" in output
    assert "Authors" in output
    assert "Similarity  0.910" in output
    assert "Summary" in output
