"""Application service for LLM-enriched paper recommendations."""

from evidence_graph.llm.client import OllamaClient
from evidence_graph.llm.prompt import SYSTEM_PROMPT, paper_analysis_prompt
from evidence_graph.llm.schema import PaperAnalysis
from evidence_graph.retrieval.paper_search import RecommendedPaper


class PaperSummarizer:
    def __init__(self, client: OllamaClient):
        self.client = client

    def analyze(
        self, source_title: str, source_text: str, candidate: RecommendedPaper
    ) -> PaperAnalysis | None:
        if not candidate.abstract:
            return None
        prompt = paper_analysis_prompt(source_title, source_text, candidate)
        return self.client.generate_structured(SYSTEM_PROMPT, prompt, PaperAnalysis)
