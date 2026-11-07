"""Command-line entry point for SEG paper recommendations."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import textwrap
from dataclasses import asdict
from pathlib import Path

from evidence_graph.config import PROJECT_ROOT
from evidence_graph.ingestion.pdf_reader import PDFReader
from evidence_graph.llm.client import LLMError, OllamaClient
from evidence_graph.llm.schema import PaperAnalysis
from evidence_graph.llm.summarizer import PaperSummarizer
from evidence_graph.retrieval.embeddings import (
    EmbeddingError,
    OllamaEmbeddingClient,
    SemanticReranker,
)
from evidence_graph.retrieval.paper_search import (
    OpenAlexSearch,
    PaperSearchError,
    RecommendedPaper,
    SearchFilters,
    build_search_query,
)
from evidence_graph.storage.cache import CacheError, SQLiteCache


def _terminal_width() -> int:
    return max(72, min(shutil.get_terminal_size(fallback=(88, 24)).columns, 110))


def _print_field(label: str, value: str, width: int) -> None:
    prefix = f"  {label:<11} "
    continuation = " " * len(prefix)
    lines = textwrap.wrap(
        value,
        width=max(20, width - len(prefix)),
        break_long_words=False,
        break_on_hyphens=False,
    ) or ["—"]
    print(prefix + lines[0])
    for line in lines[1:]:
        print(continuation + line)


def _format_authors(authors: tuple[str, ...]) -> str:
    if not authors:
        return "Unknown authors"
    names = ", ".join(authors[:3])
    return f"{names} et al." if len(authors) > 3 else names


def _print_results(
    source_title: str,
    query: str,
    results: list[RecommendedPaper],
    analyses: list[PaperAnalysis | None],
) -> None:
    width = _terminal_width()
    print("\nSEG · PAPER RECOMMENDATIONS")
    print("═" * width)
    _print_field("Source", source_title, width)
    _print_field("Search", query, width)
    print(f"  {'Results':<11} {len(results)}")

    if not results:
        print("\nNo recommendations matched the selected filters.")
        return

    for number, (paper, analysis) in enumerate(zip(results, analyses, strict=True), 1):
        print(f"\n{number:>2}. {paper.title}")
        print("─" * width)
        _print_field("Authors", _format_authors(paper.authors), width)
        publication = " · ".join(
            part for part in [str(paper.year) if paper.year else None, paper.venue] if part
        ) or "Unknown publication"
        _print_field("Published", publication, width)
        if paper.semantic_score is not None:
            _print_field("Similarity", f"{paper.semantic_score:.3f}", width)
        areas = analysis.research_areas if analysis else paper.areas
        _print_field("Areas", ", ".join(areas) or "Not classified", width)
        _print_field("Summary", analysis.summary if analysis else paper.summary, width)
        if analysis:
            _print_field("Relevance", analysis.relevance, width)
        _print_field("Link", paper.url, width)


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        prog="seg", description="Recommend relevant research papers from a local PDF."
    )
    command.add_argument("paper", type=Path, help="path to a text-based PDF")
    command.add_argument("--venue", help="conference or journal name (substring match)")
    command.add_argument("--from-year", type=int, help="earliest publication year")
    command.add_argument("--to-year", type=int, help="latest publication year")
    command.add_argument("--open-access", action="store_true", help="only open-access papers")
    command.add_argument("--limit", type=int, default=5, help="number of results (default: 5)")
    command.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    command.add_argument(
        "--llm", action="store_true", help="enrich results using a local Ollama model"
    )
    command.add_argument("--model", default="qwen3:8b", help="Ollama model (default: qwen3:8b)")
    command.add_argument(
        "--ollama-url", default="http://localhost:11434", help="Ollama server URL"
    )
    command.add_argument(
        "--rerank", action="store_true", help="semantically rerank results with Ollama"
    )
    command.add_argument(
        "--embedding-model", default="bge-m3", help="Ollama embedding model (default: bge-m3)"
    )
    command.add_argument(
        "--candidate-pool",
        type=int,
        default=30,
        help="OpenAlex candidates to consider when reranking (default: 30)",
    )
    command.add_argument(
        "--cache-path",
        type=Path,
        default=PROJECT_ROOT / "data" / "cache" / "seg.sqlite3",
        help="SQLite cache location (default: data/cache/seg.sqlite3)",
    )
    command.add_argument("--no-cache", action="store_true", help="disable persistent caching")
    return command


def run(args: argparse.Namespace) -> int:
    if args.limit < 1 or args.limit > 50:
        raise ValueError("--limit must be between 1 and 50")
    if args.from_year and args.to_year and args.from_year > args.to_year:
        raise ValueError("--from-year cannot be later than --to-year")
    if args.rerank and (args.candidate_pool < args.limit or args.candidate_pool > 100):
        raise ValueError("--candidate-pool must be between --limit and 100")

    source = PDFReader(args.paper).extract(max_pages=3)
    query = build_search_query(source.title, source.text)
    filters = SearchFilters(args.venue, args.from_year, args.to_year, args.open_access)
    cache = None if args.no_cache else SQLiteCache(args.cache_path)
    search_limit = args.candidate_pool if args.rerank else args.limit
    results = OpenAlexSearch(cache=cache).search(query, filters, search_limit)
    if args.rerank:
        reranker = SemanticReranker(
            OllamaEmbeddingClient(args.embedding_model, args.ollama_url, cache=cache)
        )
        results = reranker.rerank(source.title, source.text, results, args.limit)
    analyses: list[PaperAnalysis | None] = [None] * len(results)
    if args.llm:
        summarizer = PaperSummarizer(
            OllamaClient(args.model, args.ollama_url, cache=cache)
        )
        analyses = [
            summarizer.analyze(source.title, source.text, candidate)
            for candidate in results
        ]

    if args.json:
        output = []
        for paper, analysis in zip(results, analyses, strict=True):
            item = asdict(paper) | {"summary": paper.summary}
            item["llm_analysis"] = analysis.model_dump() if analysis else None
            output.append(item)
        print(json.dumps({"source": source.title, "query": query, "results": output}, indent=2))
        return 0

    _print_results(source.title, query, results, analyses)
    return 0


def main() -> None:
    args = parser().parse_args()
    try:
        raise SystemExit(run(args))
    except (
        FileNotFoundError,
        ValueError,
        PaperSearchError,
        LLMError,
        EmbeddingError,
        CacheError,
    ) as exc:
        print(f"seg: error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
