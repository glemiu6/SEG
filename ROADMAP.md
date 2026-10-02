# Scientific Evidence Graph — Roadmap

This document describes the planned development of Scientific Evidence Graph.

The project is divided into phases so that each component can be implemented, tested, and evaluated independently.

The general direction is:

```text
Scientific PDF
      │
      ▼
Document Structure
      │
      ▼
Scientific Claims
      │
      ▼
Literature Discovery
      │
      ▼
Evidence Retrieval
      │
      ▼
Relationship Classification
      │
      ▼
Evidence Graph
      │
      ├── Obsidian
      └── Web Interface
```

---

# Phase 1 — Scientific Document Parsing

Build the foundation for processing scientific PDFs.

## Goals

- [ ] Read scientific PDFs
- [ ] Extract page text
- [ ] Preserve page numbers
- [ ] Extract PDF metadata
- [ ] Detect section headings
- [ ] Identify section boundaries
- [ ] Split sections into paragraphs
- [ ] Clean extracted text
- [ ] Create structured document models
- [ ] Serialize processed papers to JSON

## Pipeline

```text
PDF
 ↓
Pages
 ↓
Sections
 ↓
Paragraphs
 ↓
Structured Paper
```

## Core Components

```text
PDFReader
SectionParser
ParagraphParser
JSONStore
IngestionPipeline
```

## Core Models

```text
Paper
Page
Section
Paragraph
```

---

# Phase 2 — Scientific Claim Extraction

Extract structured scientific statements from the parsed paper.

## Goals

- [ ] Implement a generic LLM client
- [ ] Define structured output schemas
- [ ] Extract claims from paragraphs
- [ ] Classify claim types
- [ ] Preserve source paragraphs
- [ ] Preserve source sections
- [ ] Preserve source page numbers
- [ ] Add structured-output validation
- [ ] Handle invalid LLM responses
- [ ] Store extracted claims

## Pipeline

```text
Paragraph
   │
   ▼
LLM
   │
   ▼
Structured Claim
```

## Initial Claim Types

Possible initial categories:

```text
METHOD
RESULT
HYPOTHESIS
CONCLUSION
OBSERVATION
BACKGROUND
```

The exact taxonomy can be refined later based on experimental results.

---

# Phase 3 — Scientific Literature Discovery

Use extracted claims to discover potentially relevant scientific papers.

## Goals

- [ ] Generate search queries from claims
- [ ] Integrate OpenAlex
- [ ] Integrate Semantic Scholar
- [ ] Integrate arXiv
- [ ] Integrate Crossref where useful
- [ ] Normalize paper metadata
- [ ] Deduplicate search results
- [ ] Rank candidate papers
- [ ] Cache external API results
- [ ] Store discovered paper metadata

## Pipeline

```text
Claim
 ↓
Search Query
 ↓
Scientific Search APIs
 ↓
Candidate Papers
```

## Candidate Metadata

Each discovered paper should ideally contain:

```text
ID
Title
Authors
Abstract
Publication Date
DOI
External URLs
Source
```

---

# Phase 4 — Semantic Evidence Retrieval

Find the most relevant evidence inside candidate papers.

## Goals

- [ ] Generate paragraph embeddings
- [ ] Generate claim embeddings
- [ ] Build local vector indexes
- [ ] Search candidate passages
- [ ] Rank passages by similarity
- [ ] Implement reranking
- [ ] Compare different retrieval strategies
- [ ] Preserve passage source information
- [ ] Return evidence with page and section references

## Pipeline

```text
Original Claim
      │
      ▼
Embedding
      │
      ▼
Candidate Passages
      │
      ▼
Reranker
      │
      ▼
Relevant Evidence
```

## Retrieval Strategies to Compare

```text
Abstract-level retrieval
Paragraph-level retrieval
Claim-level retrieval
```

Possible metrics:

```text
Precision@K
Recall@K
MRR
nDCG
```

---

# Phase 5 — Scientific Relationship Classification

Determine how two pieces of scientific evidence are related.

## Goals

- [ ] Compare pairs of claims
- [ ] Define relationship schema
- [ ] Classify relationships
- [ ] Produce confidence scores
- [ ] Generate explanations
- [ ] Preserve supporting passages
- [ ] Reject insufficient evidence
- [ ] Benchmark multiple models

## Initial Relationships

```text
SUPPORTS
CONTRADICTS
EXTENDS
RELATED
UNRELATED
```

## Pipeline

```text
Claim A
   +
Claim B
   │
   ▼
Relationship Classifier
   │
   ▼
Relationship
```

Each relationship should ideally include:

```text
source claim
target claim
relationship type
confidence
evidence
explanation
```

---

# Phase 6 — Scientific Evidence Graph

Convert papers, claims, and relationships into a graph representation.

## Goals

- [ ] Create paper nodes
- [ ] Create claim nodes
- [ ] Create directed relationships
- [ ] Store edge metadata
- [ ] Add source evidence to relationships
- [ ] Serialize graphs
- [ ] Traverse related claims
- [ ] Traverse related papers
- [ ] Find evidence paths
- [ ] Support graph expansion

## Initial Graph

```text
Paper A
  │
  └── HAS_CLAIM
          │
          ▼
       Claim A
          │
          ├── SUPPORTS ─────→ Claim B
          ├── CONTRADICTS ──→ Claim C
          └── EXTENDS ──────→ Claim D
```

## Possible Future Node Types

```text
Paper
Claim
Method
Dataset
Experiment
Result
Author
```

## Possible Future Edge Types

```text
HAS_CLAIM
SUPPORTS
CONTRADICTS
EXTENDS
RELATED
USES_METHOD
USES_DATASET
CITES
REPLICATES
```

---

# Phase 7 — Obsidian Integration

Allow users to explore the evidence graph through Obsidian.

## Goals

- [ ] Generate paper Markdown files
- [ ] Generate claim Markdown files
- [ ] Generate internal links
- [ ] Add relationship metadata
- [ ] Add source links
- [ ] Generate an Obsidian-ready vault
- [ ] Support Obsidian graph view

## Example

```text
vault/
│
├── papers/
│   ├── Paper A.md
│   └── Paper B.md
│
└── claims/
    ├── Claim A1.md
    ├── Claim A2.md
    └── Claim B1.md
```

Example note:

```markdown
# Paper A

## Claims

- [[Claim A1]]
- [[Claim A2]]

## Related Papers

- [[Paper B]]
- [[Paper C]]
```

---

# Phase 8 — Web Interface

Build an interface for interacting with the evidence graph.

Possible stack:

```text
React
  │
  ▼
FastAPI
  │
  ▼
Scientific Evidence Graph
```

## Goals

- [ ] Upload papers
- [ ] View parsed document structure
- [ ] Inspect extracted claims
- [ ] Inspect discovered papers
- [ ] Inspect relationship evidence
- [ ] Search claims
- [ ] Search papers
- [ ] Visualize the graph
- [ ] Expand graph nodes interactively
- [ ] Filter relationships
- [ ] Navigate back to source passages

---

# Phase 9 — Research Evaluation

Turn the system into an experimental research platform.

## Retrieval Experiments

Compare:

```text
Abstract Retrieval
vs
Paragraph Retrieval
vs
Claim Retrieval
```

Metrics:

```text
Precision@K
Recall@K
MRR
nDCG
```

---

## Embedding Experiments

Compare multiple scientific and general-purpose embedding models.

Evaluate:

```text
retrieval quality
latency
memory usage
index size
```

---

## Relationship Classification Experiments

Compare models on:

```text
SUPPORTS
CONTRADICTS
EXTENDS
RELATED
UNRELATED
```

Metrics:

```text
Accuracy
Precision
Recall
F1
Confusion Matrix
```

---

## LLM Benchmarking

Possible dimensions:

```text
extraction quality
classification quality
latency
token usage
memory usage
cost
```

---

## Document Structure Experiments

Compare:

```text
fixed token chunks
vs
paragraph-based chunks
vs
section-aware paragraphs
```

Possible research question:

> Does preserving scientific document structure improve claim extraction and evidence retrieval?

---

# Phase 10 — Advanced Evidence Analysis

Potential future research directions.

## Claim Clustering

Group similar claims across papers.

```text
Claim A ─┐
Claim B ─┼── Claim Cluster
Claim C ─┘
```

---

## Evidence Consensus

Estimate how scientific evidence is distributed around a claim.

For example:

```text
Central Claim
├── 8 supporting papers
├── 2 contradicting papers
└── 4 related papers
```

The system should expose the underlying evidence rather than reducing this automatically to a simple truth score.

---

## Temporal Analysis

Study how evidence changes over time.

```text
2018 → Initial Claim

2020 → Supporting Evidence

2022 → Contradictory Study

2025 → Replication

2027 → Updated Method
```

---

## Graph-Based Search

Allow queries such as:

```text
Find papers that contradict claims
supported by Paper A.
```

or:

```text
Find methods that extend Method X.
```

---

# Research Questions

Possible questions that could later form the basis of a paper include:

### RQ1

Does claim-level retrieval identify relevant scientific literature more effectively than abstract-level retrieval?

### RQ2

Does preserving document structure improve scientific claim extraction?

### RQ3

Can language models reliably classify relationships between scientific claims?

### RQ4

Which embedding models work best for claim-level scientific retrieval?

### RQ5

Does reranking significantly improve claim-to-evidence retrieval?

### RQ6

Can a claim-centered evidence graph improve scientific literature exploration compared with conventional semantic search?

---

# Long-Term Direction

The long-term objective is to move from:

```text
Paper
 ↓
Find Similar Papers
```

toward:

```text
Paper
 ↓
Understand Claims
 ↓
Discover Evidence
 ↓
Understand Relationships
 ↓
Build Scientific Knowledge Network
```

The graph should remain grounded in the original literature so that relationships can always be traced back to the evidence that produced them.