"""Local embeddings and semantic reranking through Ollama."""

from __future__ import annotations

import json
import math
from dataclasses import replace
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from evidence_graph.retrieval.paper_search import RecommendedPaper
from evidence_graph.storage.cache import SQLiteCache


class EmbeddingError(RuntimeError):
    """Raised when embeddings cannot be generated or compared."""


class OllamaEmbeddingClient:
    def __init__(
        self,
        model: str = "bge-m3",
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
        cache: SQLiteCache | None = None,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.cache = cache

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        results: list[list[float] | None] = [None] * len(texts)
        missing_indices = []
        missing_texts = []
        for index, text in enumerate(texts):
            cache_inputs = self._cache_inputs(text)
            cached = self.cache.get("ollama.embedding.v1", cache_inputs) if self.cache else None
            if cached is None:
                missing_indices.append(index)
                missing_texts.append(text)
            else:
                results[index] = cached

        if missing_texts:
            response = self._post(
                "/api/embed",
                {"model": self.model, "input": missing_texts, "truncate": True},
            )
            embeddings = response.get("embeddings")
            if not isinstance(embeddings, list) or len(embeddings) != len(missing_texts):
                raise EmbeddingError("Ollama returned an invalid number of embeddings")
            if any(not isinstance(vector, list) or not vector for vector in embeddings):
                raise EmbeddingError("Ollama returned an invalid embedding vector")
            for index, text, vector in zip(
                missing_indices, missing_texts, embeddings, strict=True
            ):
                results[index] = vector
                if self.cache:
                    self.cache.set(
                        "ollama.embedding.v1", self._cache_inputs(text), vector
                    )

        if any(vector is None for vector in results):
            raise EmbeddingError("An embedding result is missing")
        return [vector for vector in results if vector is not None]

    def _cache_inputs(self, text: str) -> dict[str, str]:
        return {"base_url": self.base_url, "model": self.model, "text": text}

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.load(response)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise EmbeddingError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError) as exc:
            raise EmbeddingError(
                f"Could not reach Ollama at {self.base_url}. Is `ollama serve` running?"
            ) from exc
        except json.JSONDecodeError as exc:
            raise EmbeddingError("Ollama returned a non-JSON response") from exc


class SemanticReranker:
    def __init__(self, client: OllamaEmbeddingClient):
        self.client = client

    def rerank(
        self,
        source_title: str,
        source_text: str,
        candidates: list[RecommendedPaper],
        limit: int,
    ) -> list[RecommendedPaper]:
        rankable = [candidate for candidate in candidates if candidate.abstract]
        unavailable = [candidate for candidate in candidates if not candidate.abstract]
        if not rankable:
            return unavailable[:limit]

        source = f"{source_title}\n\n{source_text[:12000]}"
        candidate_texts = [
            f"{candidate.title}\n\n{candidate.abstract[:12000]}"
            for candidate in rankable
        ]
        vectors = self.client.embed([source, *candidate_texts])
        source_vector, candidate_vectors = vectors[0], vectors[1:]
        scored = [
            replace(candidate, semantic_score=_cosine_similarity(source_vector, vector))
            for candidate, vector in zip(rankable, candidate_vectors, strict=True)
        ]
        scored.sort(
            key=lambda candidate: (
                candidate.semantic_score
                if candidate.semantic_score is not None
                else -1.0
            ),
            reverse=True,
        )
        return (scored + unavailable)[:limit]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise EmbeddingError("Embedding dimensions do not match")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        raise EmbeddingError("Cannot compare a zero-length embedding")
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)
