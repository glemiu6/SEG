import pytest
from pydantic import ValidationError

from evidence_graph.models.schema import Span, Paper, Paragraph, SectionType,Section


def test_valid_span():
    s = Span(paper_id="p1", text="abc", char_start=2, char_end=5)
    assert s.text == "abc"


def test_offsets_optional():
    Span(paper_id="p1", text="abc")


def test_length_must_match_offsets():
    with pytest.raises(ValidationError):
        Span(paper_id="p1", text="abc", char_start=0, char_end=10)


def test_offsets_come_together():
    with pytest.raises(ValidationError):
        Span(paper_id="p1", text="abc", char_start=0)


def make_paper() -> Paper:
    para = Paragraph(id="p1:s1:p0", section_id="p1:s1", text="We show that X improves Y.")
    sec = Section(id="p1:s1", heading="Results", type=SectionType.RESULTS, paragraphs=[para])
    return Paper(id="p1", title="A Paper", sections=[sec], parse_source="test")


def test_paper_roundtrip():
    paper = make_paper()
    again = Paper.model_validate_json(paper.model_dump_json())
    assert again == paper


def test_enum_saved_as_plain_string():
    assert '"type":"results"' in make_paper().model_dump_json().replace(" ", "")