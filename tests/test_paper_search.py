from evidence_graph.retrieval.paper_search import (
    OpenAlexSearch,
    SearchFilters,
    build_search_query,
    exclude_source_and_duplicates,
)
from evidence_graph.retrieval.paper_search import RecommendedPaper


def test_decode_openalex_abstract():
    assert OpenAlexSearch._decode_abstract({"world": [1], "Hello": [0]}) == "Hello world"
    assert OpenAlexSearch._decode_abstract(None) is None


def test_api_filters():
    filters = SearchFilters(from_year=2020, to_year=2024, open_access=True)
    assert OpenAlexSearch._api_filters(filters) == [
        "from_publication_date:2020-01-01",
        "to_publication_date:2024-12-31",
        "is_oa:true",
    ]


def test_query_uses_informative_frequent_terms():
    query = build_search_query("Graph Retrieval", "Graph graph evidence retrieval. This paper shows results.")
    assert query.split()[:3] == ["graph", "retrieval", "evidence"]


def test_summary_is_bounded_when_abstract_has_no_sentence_spaces():
    paper = RecommendedPaper(
        title="Title", authors=(), year=None, venue=None, url="", doi=None,
        abstract="First sentence.Second " + "word " * 150,
        areas=(), citation_count=0, score=1.0,
    )
    assert len(paper.summary) <= 500
    assert paper.summary.endswith("...")


def recommendation(title: str, doi: str | None = None) -> RecommendedPaper:
    return RecommendedPaper(
        title=title, authors=(), year=None, venue=None, url="", doi=doi,
        abstract="Abstract", areas=(), citation_count=0, score=1.0,
    )


def test_excludes_source_by_normalized_title():
    candidates = [
        recommendation("Graph Retrieval: Augmented Generation"),
        recommendation("A Different Paper"),
    ]
    results = exclude_source_and_duplicates(
        "Graph Retrieval — Augmented Generation", candidates, 5
    )
    assert [paper.title for paper in results] == ["A Different Paper"]


def test_deduplicates_doi_and_title_while_preserving_rank():
    candidates = [
        recommendation("First version", "https://doi.org/10.1/example"),
        recommendation("Published version", "doi:10.1/example"),
        recommendation("Same Title"),
        recommendation("same-title"),
        recommendation("Unique"),
    ]
    results = exclude_source_and_duplicates("Source", candidates, 10)
    assert [paper.title for paper in results] == ["First version", "Same Title", "Unique"]


def test_deduplication_respects_limit():
    candidates = [recommendation("One"), recommendation("Two"), recommendation("Three")]
    assert len(exclude_source_and_duplicates("Source", candidates, 2)) == 2
