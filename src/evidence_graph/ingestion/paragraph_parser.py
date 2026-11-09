import re

from evidence_graph.models.schema import Paragraph

class ParagraphParser:

    def parse(self, text: str, paper_id: str, section_id: str = "body") -> list[Paragraph]:
        """Return cleaned, addressable paragraphs from extracted PDF text."""
        paragraphs: list[Paragraph] = []
        for index, raw in enumerate(self.split_paragraph(text)):
            cleaned = self.clean_paragraph(raw)
            if cleaned:
                paragraphs.append(
                    Paragraph(id=f"{paper_id}:{section_id}:{index}", section_id=section_id, text=cleaned)
                )
        return paragraphs

    def split_paragraph(self, text: str) -> list[str]:
        return re.split(r"\n\s*\n",text)

    def clean_paragraph(self, text: str) -> str:
        lines = text.splitlines()

        lines = [
            line.strip()
            for line in lines
            if line.strip()
        ]
        return " ".join(lines)
