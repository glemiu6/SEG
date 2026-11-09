"""Dependency-free lexical retrieval over parsed evidence passages.

This intentionally small baseline makes the evidence workflow usable before a
domain embedding index is introduced. It is deterministic and easy to evaluate.
"""

from __future__ import annotations

import math
import re
from collections import Counter

from evidence_graph.models.schema import Span


TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")
STOPWORDS = frozenset({"the", "and", "for", "with", "that", "this", "from", "are", "was", "were", "into", "than", "using", "our", "their", "has", "have"})


def tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text) if token.lower() not in STOPWORDS]


class EvidenceSearcher:
    def __init__(self, passages: list[Span]):
        self.passages = passages
        self._documents = [Counter(tokens(passage.text)) for passage in passages]
        self._document_frequency = Counter(
            token for document in self._documents for token in document
        )

    def search(self, query: str, limit: int = 5) -> list[Span]:
        query_counts = Counter(tokens(query))
        scores: list[tuple[float, int]] = []
        total = max(len(self._documents), 1)
        for index, document in enumerate(self._documents):
            score = sum(
                frequency * (math.log((total + 1) / (self._document_frequency[token] + 1)) + 1)
                for token, frequency in query_counts.items() if token in document
            ) / math.sqrt(sum(value * value for value in document.values()) or 1)
            if score:
                scores.append((score, index))
        return [self.passages[index] for _, index in sorted(scores, reverse=True)[:limit]]
