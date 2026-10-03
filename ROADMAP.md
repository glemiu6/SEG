# ROADMAP

**Research question (primary):** Does claim-level retrieval find contradicting and qualifying evidence better than abstract- or paper-level retrieval?

**Secondary questions**
- RQ2: Does structure-preserving parsing improve claim extraction quality?
- RQ3: Can LLMs classify claim-to-evidence stance reliably, after conditions are compared?

**Principles:** vertical slice first, evaluate before scaling, every stage writes versioned JSON artifacts, nothing without provenance.

Time estimates assume ~10 hrs/week. Adjust, but keep the order.

---

## M0: Foundations (week 1)
- Pydantic schema (`schema.py`), `SCHEMA_VERSION`, JSON store
- Config, logging, LLM client with disk cache and pinned model/prompt versions
- Tests for schema round-trips

**Exit:** a `Paper` and `Claim` serialize, load, and validate.

## M1: Parsing (weeks 2–3)
- Implement the pipeline in `PARSING.md`: arXiv LaTeX/HTML first, GROBID second
- Section normalizer, paragraph and citation-mention extraction, validators
- Compare GROBID vs Docling vs PyMuPDF on 30 hand-checked papers

**Exit:** ≥ 95% of corpus papers parse; section-type accuracy ≥ 90%; span validation 100%.

## M2: Corpus + claim extraction (weeks 3–5)
- Pick **one narrow topic** (for example, LLM routing, or retrieval evaluation). Build a fixed corpus of 1,000 open-access papers, later 5–50k.
- Check-worthiness filter
- Claim extractor with decontextualization and structured slots
- Manual review of 100 extracted claims: precision, self-containedness, slot accuracy

**Exit:** ≥ 85% of reviewed claims judged self-contained and faithful. Record failure types.

## M3: Gold set + baselines (weeks 5–8) ⟵ most important
- **Benchmarks (sanity):** SciFact, SciFact-Open, SciCite; optionally SciRIFF and Citation-intent sets
- **Own gold set:** ~200–300 claim/passage pairs sampled from your corpus, labeled `supports / contradicts / qualifies / neutral / not-relevant` by two annotators. Report Cohen's κ and adjudicate disagreements. Oversample contradictions (they are rare; mine them with citation contexts containing "however", "in contrast", "fails to replicate").
- **Retrieval baselines:** BM25, SPECTER2 (abstract level), dense paragraph retrieval, dense claim-to-claim retrieval, hybrid + cross-encoder reranker
- **Stance baselines:** off-the-shelf NLI model, fine-tuned SciFact model, zero-shot LLM, LLM with condition-match step

**Metrics**
| Task | Metrics |
|---|---|
| Retrieval | Recall@k, MRR, nDCG@10; **contradiction-recall@k** reported separately |
| Stance | macro-F1, per-class F1 (contradicts and qualifies especially), confusion matrix |
| Claim extraction | precision, self-containedness rate, slot accuracy |
| Parsing | section accuracy, citation resolution rate |

**Exit:** a results table with all baselines and confidence intervals (bootstrap). If claim-level retrieval does not beat abstract-level, that is still a publishable finding.

## M4: Vertical slice end-to-end (weeks 8–10)
`1 paper → ~10 claims → retrieve from the 1,000-paper corpus → rerank → condition match → stance → graph JSON`

- Edge schema with evidence span, rationale, confidence
- Paper-level relations from metadata: `CITES`, `SAME_DATASET` (dataset name normalization), `SAME_METHOD`
- NetworkX graph builder and JSON export
- Cost and latency log per paper

**Exit:** one paper produces a graph where every edge opens to an exact evidence quote.

## M5: Improve + ablate (weeks 10–14)
Ablations (each one a table row):
1. Abstract vs paragraph vs claim retrieval
2. Structure-preserving vs flat parsing
3. Raw claim vs decontextualized claim
4. With vs without condition-match step
5. Embedding models A/B (SPECTER2, general-purpose embedder, domain-tuned)
6. Citation contexts as weak supervision: fine-tune retriever or stance model on them

Error analysis: sample 50 failures per stage and categorize.

**Exit:** each ablation reported, with conclusions you'd defend to a reviewer.

## M6: Human review + minimal UI (weeks 14–16)
- Simple review tool (Streamlit or a local HTML page): show claim, evidence, stance, accept/correct
- Corrections write `human_label` and feed the gold set
- Graph visualization (pyvis/Cytoscape.js export), screenshot for README

**Exit:** can review 50 edges in 15 minutes; corrections reload into evaluation.

## M7: Write-up and release (weeks 16–20)
- Paper draft: motivation, related work (SciFact, scite, citation intent, ORKG), method, benchmark, results, limitations
- Release: code, corpus IDs, gold annotations (check licenses), prompts, cached outputs
- README with demo, results table, and reproduction commands

---

## Deferred (add only if the above works)
- `EXTENDS` relation (needs citation + method evidence)
- Obsidian export
- FastAPI + React
- FAISS (switch from brute force when corpus > ~100k passages)
- Live API search (OpenAlex, Semantic Scholar) as an online mode
- Table and figure-based claims

## Risks
| Risk | Mitigation |
|---|---|
| Claims too vague to compare | Decontextualization + slot extraction; measure self-containedness |
| Few true contradictions in corpus | Mine via citation contexts; include SciFact-Open and replication papers |
| LLM cost | Check-worthiness filter, cache, small model for filtering, large for stance |
| Annotation agreement low | Refine taxonomy early; pilot on 30 pairs |
| Parser failures | Source priority, validators, failure log |
| Scope creep | Each milestone has exit criteria; defer list above |

## Definition of done for v0.1
- Reproducible command that builds a graph for the sample corpus
- Results table with ≥ 4 retrieval and ≥ 3 stance baselines
- Gold set with reported κ
- Every edge traceable to page, paragraph, and exact span