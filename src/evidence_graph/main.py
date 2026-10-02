import sys

from evidence_graph.config import AppConfig
from evidence_graph.ingestion.pdf_reader import PDFReader
from evidence_graph.models.document import Page


def main():
    config = AppConfig()

    filename = sys.argv[1]

    pdf_path = config.papers_dir / filename

    if not pdf_path.exists():
        raise FileNotFoundError(f"Paper not found: {pdf_path}")

    reader = PDFReader(pdf_path)

    print(reader.extract_metadata())

    pages = reader.extract_pages()

    for page in pages[:1]:
        print(f"\nPAGE: {page.number}")

        for block_number, block in enumerate(page.blocks):
            print(f"\nBLOCK: {block_number}")

            for line_number, line in enumerate(block.lines):
                print(f"  LINE: {line_number}")

                for span in line.spans:
                    print(
                        f"    {span.text!r} | font={span.font} | size={span.size:.1f}"
                    )


if __name__ == "__main__":
    main()