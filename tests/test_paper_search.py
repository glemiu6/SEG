from evidence_graph.retrieval.paper_search import OpenAlexSearch, SearchFilters, build_search_query
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
