import json

import pytest

from evidence_graph.llm.client import LLMError, OllamaClient
from evidence_graph.llm.schema import PaperAnalysis
from evidence_graph.llm.summarizer import PaperSummarizer
from evidence_graph.retrieval.paper_search import RecommendedPaper


def paper(abstract: str | None = "An abstract") -> RecommendedPaper:
    return RecommendedPaper(
        title="Candidate", authors=(), year=2025, venue=None, url="", doi=None,
        abstract=abstract, areas=("Retrieval",), citation_count=0, score=1.0,
    )


def test_ollama_client_validates_structured_response(monkeypatch):
    client = OllamaClient()
    monkeypatch.setattr(
        client,
        "_post",
        lambda path, payload: {
            "message": {
                "content": json.dumps({
                    "summary": "A concise summary.",
                    "research_areas": ["Information retrieval"],
                    "relevance": "It studies a related retrieval method.",
                })
            }
        },
    )
    result = client.generate_structured("system", "user", PaperAnalysis)
    assert result.research_areas == ["Information retrieval"]


def test_ollama_client_rejects_invalid_output(monkeypatch):
    client = OllamaClient()
    monkeypatch.setattr(client, "_post", lambda path, payload: {"message": {"content": "{}"}})
    with pytest.raises(LLMError, match="invalid structured output"):
        client.generate_structured("system", "user", PaperAnalysis)


def test_summarizer_skips_candidates_without_abstract():
    class UnexpectedClient:
        def generate_structured(self, *args):
            raise AssertionError("the model must not be called")

    assert PaperSummarizer(UnexpectedClient()).analyze("Source", "Text", paper(None)) is None
