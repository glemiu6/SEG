from evidence_graph.extraction.claims import ClaimExtractor, ClaimExtractionResult, ExtractedClaim


class FakeClient:
    def generate_structured(self, system_prompt, user_prompt, output_model):
        return ClaimExtractionResult(claims=[ExtractedClaim(
            text="The method improves accuracy.", evidence_quote="The method improves accuracy.",
            conditions=["tested dataset"], confidence=0.8,
        )])


def test_claim_extractor_preserves_exact_quote_offsets():
    text = "Introduction. The method improves accuracy. Conclusion."
    claims = ClaimExtractor(FakeClient()).extract("source", text)
    assert len(claims) == 1
    assert claims[0].source_span.text == "The method improves accuracy."
    assert text[claims[0].source_span.char_start:claims[0].source_span.char_end] == claims[0].source_span.text


def test_claim_extractor_discards_non_provenanced_output():
    class InvalidQuoteClient:
        def generate_structured(self, *args):
            return ClaimExtractionResult(claims=[ExtractedClaim(
                text="Claim", evidence_quote="not in source", confidence=0.5,
            )])

    assert ClaimExtractor(InvalidQuoteClient()).extract("source", "Real source text.") == []
