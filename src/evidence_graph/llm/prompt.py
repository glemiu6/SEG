"""Prompts for analyzing a recommendation against an uploaded paper."""

from evidence_graph.retrieval.paper_search import RecommendedPaper


SYSTEM_PROMPT = """You analyze academic-paper recommendations.
Use only the supplied titles and text. Do not invent findings or details.
Return JSON matching the supplied schema. Write a concise, plain-language summary,
list 1-5 research areas, and explain why the candidate is relevant to the source.
If evidence is limited, say so explicitly."""


def paper_analysis_prompt(
    source_title: str,
    source_text: str,
    candidate: RecommendedPaper,
    max_source_chars: int = 6000,
    max_abstract_chars: int = 8000,
) -> str:
    areas = ", ".join(candidate.areas) or "Not classified"
    return f"""SOURCE PAPER
Title: {source_title}
Opening text:
{source_text[:max_source_chars]}

CANDIDATE PAPER
Title: {candidate.title}
Abstract:
{(candidate.abstract or 'No abstract available.')[:max_abstract_chars]}
OpenAlex topics: {areas}

Analyze the candidate paper and its relevance to the source paper."""
