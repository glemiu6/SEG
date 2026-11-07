"""Small, local PDF text extractor used by the recommendation CLI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pymupdf


@dataclass(frozen=True)
class ExtractedPaper:
    path: Path
    title: str
    authors: str | None
    text: str


class PDFReader:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.is_file():
            raise FileNotFoundError(f"Paper not found: {self.path}")
        if self.path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file: {self.path}")

    def extract(self, max_pages: int | None = None) -> ExtractedPaper:
        with pymupdf.open(self.path) as document:
            if document.needs_pass:
                raise ValueError("Encrypted PDFs are not supported")
            metadata = document.metadata or {}
            pages = document if max_pages is None else document[:max_pages]
            text = "\n".join(page.get_text("text", sort=True) for page in pages)

        text = "\n".join(line.rstrip() for line in text.splitlines()).strip()
        if not text:
            raise ValueError(
                "No selectable text was found. Scanned PDFs require OCR, which is "
                "not included in the first MVP."
            )
        title = (metadata.get("title") or "").strip() or self._title_from_text(text)
        authors = (metadata.get("author") or "").strip() or None
        return ExtractedPaper(self.path, title, authors, text)

    def extract_metadata(self) -> dict[str, str]:
        paper = self.extract(max_pages=1)
        return {"title": paper.title, "author": paper.authors or "Unknown"}

    def extract_text(self, max_pages: int | None = None) -> str:
        return self.extract(max_pages=max_pages).text

    @staticmethod
    def _title_from_text(text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return " ".join(lines[:2])[:300] if lines else "Untitled paper"
