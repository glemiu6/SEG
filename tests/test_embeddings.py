import pytest

from evidence_graph.retrieval.embeddings import (
    EmbeddingError,
    OllamaEmbeddingClient,
    SemanticReranker,
    _cosine_similarity,
)
from evidence_graph.retrieval.paper_search import RecommendedPaper
from evidence_graph.storage.cache import SQLiteCache


def paper(title: str, abstract: str | None) -> RecommendedPaper:
    return RecommendedPaper(
        title=title, authors=(), year=2025, venue=None, url="", doi=None,
        abstract=abstract, areas=(), citation_count=0, score=1.0,
    )


def test_embedding_client_validates_batch_size(monkeypatch):
    client = OllamaEmbeddingClient()
    monkeypatch.setattr(client, "_post", lambda path, payload: {"embeddings": [[1.0]]})
    with pytest.raises(EmbeddingError, match="number of embeddings"):
        client.embed(["one", "two"])


def test_embedding_client_reuses_individual_cached_texts(monkeypatch, tmp_path):
    client = OllamaEmbeddingClient(cache=SQLiteCache(tmp_path / "cache.sqlite3"))
    calls = []

    def fake_post(path, payload):
        calls.append(payload["input"])
        return {"embeddings": [[float(len(text))] for text in payload["input"]]}

    monkeypatch.setattr(client, "_post", fake_post)
    assert client.embed(["one", "two"]) == [[3.0], [3.0]]
    assert client.embed(["two", "three"]) == [[3.0], [5.0]]
    assert calls == [["one", "two"], ["three"]]


def test_cosine_similarity():
    assert _cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert _cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_reranker_orders_by_semantic_similarity():
    class FakeClient:
        def embed(self, texts):
            assert len(texts) == 3
            return [[1.0, 0.0], [0.0, 1.0], [0.9, 0.1]]

    candidates = [paper("Unrelated", "Text"), paper("Relevant", "Text")]
    results = SemanticReranker(FakeClient()).rerank("Source", "Text", candidates, 2)
    assert [result.title for result in results] == ["Relevant", "Unrelated"]
    assert results[0].semantic_score > results[1].semantic_score


def test_reranker_puts_missing_abstract_last():
    class FakeClient:
        def embed(self, texts):
            return [[1.0], [1.0]]

    results = SemanticReranker(FakeClient()).rerank(
        "Source", "Text", [paper("Missing", None), paper("Available", "Text")], 2
    )
    assert [result.title for result in results] == ["Available", "Missing"]
