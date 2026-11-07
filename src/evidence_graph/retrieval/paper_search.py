"""OpenAlex-backed discovery and lightweight recommendation ranking."""

from __future__ import annotations

import json
import re
import ssl
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

from evidence_graph.storage.cache import SQLiteCache


OPENALEX_URL = "https://api.openalex.org/works"
USER_AGENT = "SEG/0.1 (https://github.com/glemiu6/SEG)"


@dataclass(frozen=True)
class SearchFilters:
    venue: str | None = None
    from_year: int | None = None
    to_year: int | None = None
    open_access: bool = False


@dataclass(frozen=True)
class RecommendedPaper:
    title: str
    authors: tuple[str, ...]
    year: int | None
    venue: str | None
    url: str
    doi: str | None
    abstract: str | None
    areas: tuple[str, ...]
    citation_count: int
    score: float
    semantic_score: float | None = None

    @property
    def summary(self) -> str:
        if not self.abstract:
            return "No abstract is available from OpenAlex."
        abstract = re.sub(r"\s+", " ", self.abstract).strip()
        sentences = re.split(r"(?<=[.!?])(?:\s+|(?=[A-Z]))", abstract)
        summary = " ".join(sentences[:2])
        if len(summary) <= 500:
            return summary
        shortened = summary[:497].rsplit(" ", 1)[0]
        return f"{shortened}..."


class PaperSearchError(RuntimeError):
    pass


class OpenAlexSearch:
    def __init__(self, timeout: float = 20.0, cache: SQLiteCache | None = None):
        self.timeout = timeout
        self.cache = cache

    def search(
        self, query: str, filters: SearchFilters, limit: int = 10
    ) -> list[RecommendedPaper]:
        params: dict[str, str | int] = {
            "search": query,
            "per-page": min(max(limit * 3, 25), 100),
            "select": (
                "id,doi,display_name,publication_year,authorships,primary_location,"
                "open_access,abstract_inverted_index,topics,cited_by_count,relevance_score"
            ),
        }
        api_filters = self._api_filters(filters)
        if api_filters:
            params["filter"] = ",".join(api_filters)
        request = Request(
            f"{OPENALEX_URL}?{urlencode(params)}",
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )
        cache_inputs = {"url": request.full_url}
        payload = self.cache.get("openalex.search.v1", cache_inputs) if self.cache else None
        if payload is None:
            try:
                tls = ssl.create_default_context(cafile=certifi.where())
                with urlopen(request, timeout=self.timeout, context=tls) as response:
                    payload = json.load(response)
            except HTTPError as exc:
                raise PaperSearchError(f"OpenAlex returned HTTP {exc.code}") from exc
            except (URLError, TimeoutError, json.JSONDecodeError) as exc:
                raise PaperSearchError(f"Could not reach OpenAlex: {exc}") from exc
            if self.cache:
                self.cache.set("openalex.search.v1", cache_inputs, payload, ttl_seconds=86400)

        papers = [self._paper(item) for item in payload.get("results", [])]
        if filters.venue:
            needle = filters.venue.casefold()
            papers = [p for p in papers if needle in (p.venue or "").casefold()]
        return papers[:limit]

    @staticmethod
    def _api_filters(filters: SearchFilters) -> list[str]:
        values = []
        if filters.from_year:
            values.append(f"from_publication_date:{filters.from_year}-01-01")
        if filters.to_year:
            values.append(f"to_publication_date:{filters.to_year}-12-31")
        if filters.open_access:
            values.append("is_oa:true")
        return values

    @classmethod
    def _paper(cls, item: dict[str, Any]) -> RecommendedPaper:
        location = item.get("primary_location") or {}
        source = location.get("source") or {}
        authors = tuple(
            a.get("author", {}).get("display_name", "Unknown")
            for a in item.get("authorships") or []
        )
        topics = tuple(
            topic.get("display_name", "")
            for topic in (item.get("topics") or [])[:3]
            if topic.get("display_name")
        )
        doi = item.get("doi")
        url = doi or location.get("landing_page_url") or item.get("id") or ""
        return RecommendedPaper(
            title=item.get("display_name") or "Untitled",
            authors=authors,
            year=item.get("publication_year"),
            venue=source.get("display_name"),
            url=url,
            doi=doi,
            abstract=cls._decode_abstract(item.get("abstract_inverted_index")),
            areas=topics,
            citation_count=item.get("cited_by_count") or 0,
            score=float(item.get("relevance_score") or 0.0),
        )

    @staticmethod
    def _decode_abstract(index: dict[str, list[int]] | None) -> str | None:
        if not index:
            return None
        words = [(position, word) for word, positions in index.items() for position in positions]
        return " ".join(word for _, word in sorted(words))


def build_search_query(title: str, text: str, max_terms: int = 14) -> str:
    """Use the title plus frequent informative words from the abstract/first page."""
    stopwords = {
        "about", "after", "also", "among", "based", "been", "being", "between",
        "both", "could", "from", "have", "into", "more", "most", "other", "paper",
        "results", "show", "such", "than", "that", "their", "these", "this", "through",
        "using", "were", "which", "with", "would", "your", "abstract", "introduction",
    }
    tokens = re.findall(r"[A-Za-z][A-Za-z-]{3,}", f"{title} {text[:6000]}".lower())
    counts: dict[str, int] = {}
    for token in tokens:
        if token not in stopwords:
            counts[token] = counts.get(token, 0) + 1
    terms = sorted(counts, key=lambda word: (-counts[word], word))[:max_terms]
    return " ".join(terms) or title
