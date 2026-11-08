from evidence_graph.ingestion.pdf_reader import extract_abstract


def test_extract_abstract_between_section_headings():
    text = """A Paper Title
Ada Author
Abstract
We introduce a semantic retrieval system for scientific papers.
It improves recommendation quality using local embeddings.
1 Introduction
The rest of the paper begins here.
"""
    assert extract_abstract(text) == (
        "We introduce a semantic retrieval system for scientific papers. "
        "It improves recommendation quality using local embeddings."
    )


def test_extract_abstract_supports_inline_ieee_style():
    text = """Title
Abstract—This paper presents a sufficiently detailed method for retrieving related work.
Index Terms—information retrieval, language models
"""
    assert extract_abstract(text) == (
        "This paper presents a sufficiently detailed method for retrieving related work."
    )


def test_extract_abstract_returns_none_when_heading_is_missing():
    assert extract_abstract("A title\nSome introductory text without a section heading.") is None
