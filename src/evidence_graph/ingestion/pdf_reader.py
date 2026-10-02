from pathlib import Path

import pymupdf

from evidence_graph.models.document import (
    Page,
    TextBox,
    TextLine,
    TextSpan,
)


class PDFReader:

    def __init__(self,path:str):
        self.path = Path(path)

        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")

        if self.path.suffix.lower() != ".pdf":
            raise ValueError(f"Invalid file type: {self.path}")

    def extract_pages(self) -> list[Page]:
        pages = []

        with pymupdf.open(self.path) as document:
            for page_number, page in enumerate(document):
                page_data = page.get_text("dict", sort=True)

                blocks = []

                for block in page_data["blocks"]:
                    if block["type"] != 0:
                        continue

                    lines = []

                    for line in block["lines"]:
                        spans = []

                        for span in line["spans"]:
                            text = span["text"].strip()

                            if not text:
                                continue

                            spans.append(
                                TextSpan(
                                    text=text, font=span["font"], size=span["size"]
                                )
                            )

                        if spans:
                            lines.append(TextLine(bbox=line["bbox"],spans=spans))

                    if lines:
                        blocks.append(TextBox(bbox=block["bbox"],lines=lines))

                pages.append(Page(number=page_number + 1, blocks=blocks))

        return pages


    def extract_metadata(self):
        with pymupdf.open(self.path) as document:
            metadata = document.metadata

            return {
                "title": metadata.get("title") or "Untitled",
                "author": metadata.get("author") or "Unknown",
            }


if __name__ == "__main__":
    reader = PDFReader("../../../data/papers/HELM.pdf")
    print(reader.extract_metadata())
    print(reader.extract_pages())