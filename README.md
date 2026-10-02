# SEG — Scientific Evidence Graph

SEG is a research-oriented system for discovering and visualizing relationships between scientific papers at the claim level.

Rather than only finding papers that are semantically similar, SEG aims to identify how scientific work is related — for example, whether one paper supports, contradicts, extends, or otherwise relates to claims made in another.
Instead of only finding papers that are semantically similar, the system aims to understand **how scientific work is related**.

A paper may:

- support a claim made by another paper;
- contradict a result;
- extend an existing method;
- use a similar methodology;
- reuse the same dataset;
- investigate the same research problem from a different perspective.

These relationships are represented as a graph that researchers can explore.

---

## Why This Project Exists

Finding relevant scientific literature can be difficult.

Most academic search tools rely primarily on:

- keywords;
- titles;
- abstracts;
- citations;
- semantic similarity.

These approaches are useful, but they usually operate at the **paper level**.

Researchers often need more specific information:

> Which papers support this particular claim?

> Are there papers that contradict this result?

> Has another paper used this methodology in a different context?

> Which papers provide evidence related to this statement?

Two papers may be strongly related even when their titles and abstracts use very different terminology.

Scientific Evidence Graph approaches literature discovery at a more fine-grained level by breaking papers into smaller scientific units.

```text
Paper
├── Sections
├── Paragraphs
├── Claims
├── Methods
├── Datasets
└── Results
```

These units can then be compared across papers.

---

## Main Idea

The system transforms scientific literature into a structured graph of scientific evidence.

The general pipeline is:

```text
Scientific Paper
       │
       ▼
Document Parsing
       │
       ▼
Sections & Paragraphs
       │
       ▼
Claim Extraction
       │
       ▼
Scientific Literature Search
       │
       ▼
Relevant Evidence Retrieval
       │
       ▼
Relationship Classification
       │
       ▼
Scientific Evidence Graph
```

Instead of only answering:

> Which papers are similar?

the goal is to also answer:

> Why are these papers related?

---

## Example

Suppose a scientific paper contains the claim:

> Semantic similarity can be used to dynamically route requests between heterogeneous agents.

The system could:

1. extract the claim;
2. search for related scientific literature;
3. retrieve relevant passages;
4. compare the retrieved evidence with the original claim;
5. classify the relationship.

For example:

```text
                         Paper B
                            │
                         SUPPORTS
                            │
                            ▼
Paper C ── CONTRADICTS ── Claim A ── EXTENDS ── Paper D
                            │
                          RELATED
                            │
                            ▼
                         Paper E
```

Possible relationships include:

```text
SUPPORTS
CONTRADICTS
EXTENDS
RELATED
UNRELATED
```

---

## How It Differs From Traditional RAG

Retrieval-Augmented Generation may be used as one component of the system, but retrieval itself is not the final goal.

A typical RAG pipeline looks like:

```text
Question
   │
   ▼
Retrieve Documents
   │
   ▼
LLM
   │
   ▼
Answer
```

Scientific Evidence Graph focuses on constructing structured knowledge:

```text
Paper
   │
   ▼
Understand Document
   │
   ▼
Extract Claims
   │
   ▼
Find Related Evidence
   │
   ▼
Compare Scientific Statements
   │
   ▼
Classify Relationships
   │
   ▼
Build Evidence Graph
```

RAG can therefore be used for evidence retrieval, while the larger system focuses on discovering and representing relationships between scientific claims.

---

## Core Concepts

### Paper

The original scientific document.

A paper can contain:

```text
Paper
├── Metadata
├── Pages
├── Sections
├── Paragraphs
└── Claims
```

---

### Section

The logical structure of the paper is preserved whenever possible.

Examples include:

```text
Abstract
Introduction
Related Work
Methodology
Experiments
Results
Discussion
Conclusion
```

Preserving document structure helps maintain the context in which scientific statements appear.

---

### Paragraph

Paragraphs act as meaningful textual units.

Instead of immediately splitting papers into arbitrary token chunks:

```text
Introduction
├── Paragraph 1
├── Paragraph 2
└── Paragraph 3
```

This allows later stages to retain information about the source section and surrounding context.

---

### Claim

A claim is a scientific statement extracted from a paper.

Example:

```text
"The proposed method improves routing accuracy."
```

Structured representation:

```json
{
  "text": "The proposed method improves routing accuracy.",
  "type": "result",
  "section": "Results"
}
```

Claims can then be compared with claims extracted from other papers.

---

### Relationship

Relationships describe how claims or papers are connected.

Initial relationship types include:

```text
SUPPORTS
CONTRADICTS
EXTENDS
RELATED
UNRELATED
```

These relationships become edges in the evidence graph.

---

## Architecture

```text
scientific-evidence-graph/
│
├── README.md
├── ROADMAP.md
├── pyproject.toml
├── uv.lock
├── .gitignore
│
├── src/
│   └── evidence_graph/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   └── document.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── pdf_reader.py
│       │   ├── section_parser.py
│       │   └── paragraph_parser.py
│       │
│       ├── extraction/
│       │   ├── __init__.py
│       │   └── claims.py
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── client.py
│       │   ├── prompts.py
│       │   └── schemas.py
│       │
│       ├── retrieval/
│       │   ├── __init__.py
│       │   ├── paper_search.py
│       │   └── embeddings.py
│       │
│       ├── relations/
│       │   ├── __init__.py
│       │   └── classifier.py
│       │
│       ├── graph/
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── builder.py
│       │   └── exporter.py
│       │
│       ├── storage/
│       │   ├── __init__.py
│       │   └── json_store.py
│       │
│       └── pipeline/
│           ├── __init__.py
│           └── paper_pipeline.py
│
├── data/
│   ├── papers/
│   ├── parsed/
│   ├── results/
│   └── obsidian/
│
├── tests/
│   ├── test_pdf_reader.py
│   ├── test_section_parser.py
│   ├── test_paragraph_parser.py
│   ├── test_claims.py
│   └── test_relations.py
│
└── experiments/
    ├── datasets/
    ├── results/
    └── notebooks/
```

---

## How It Works

### 1. Read a Scientific Paper

The system receives a PDF and extracts its content.

```text
paper.pdf
   │
   ▼
PDFReader
```

The parser preserves page information so extracted information can later be traced back to its source.

---

### 2. Recover Document Structure

The extracted document is divided into logical sections.

```text
Pages
  │
  ▼
SectionParser
  │
  ├── Abstract
  ├── Introduction
  ├── Methodology
  ├── Results
  └── Conclusion
```

---

### 3. Extract Paragraphs

Sections are divided into paragraphs.

```text
Methodology
│
├── Paragraph 1
├── Paragraph 2
└── Paragraph 3
```

---

### 4. Extract Scientific Claims

Selected paragraphs are analyzed and converted into structured claims.

```text
Paragraph
   │
   ▼
LLM
   │
   ▼
Structured Claims
```

---

### 5. Find Related Literature

Extracted claims are used to search scientific literature.

Possible sources include:

- OpenAlex;
- Semantic Scholar;
- Crossref;
- arXiv;
- local scientific paper collections.

---

### 6. Retrieve Evidence

Relevant passages are retrieved from candidate papers.

```text
Claim
  │
  ▼
Semantic Retrieval
  │
  ▼
Candidate Evidence
```

---

### 7. Classify Relationships

Claims are compared and assigned a relationship.

```text
Claim A + Claim B
        │
        ▼
Relationship Classifier
        │
        ▼
SUPPORTS / CONTRADICTS / EXTENDS / RELATED
```

---

### 8. Build the Evidence Graph

The resulting information becomes a directed graph.

```text
Paper A
  │
  └── HAS_CLAIM
          │
          ▼
       Claim A
          │
          ├── SUPPORTS ─────→ Claim B
          └── CONTRADICTS ──→ Claim C
```

---

## Installation

### Requirements

- Python
- uv

Clone the repository:

```bash
git clone https://github.com/glemiu6/SEG.git
cd SEG
```

Install dependencies:

```bash
uv sync
```

---

## Usage

Place a scientific paper inside:

```text
data/papers/
```

For example:

```text
data/papers/example.pdf
```

Run the pipeline:

```bash
uv run python -m evidence_graph.main data/papers/example.pdf
```

Processed document data can be stored in:

```text
data/parsed/
```

Graph and analysis results can be stored in:

```text
data/results/
```

---

## Tests

Run the test suite with:

```bash
uv run pytest
```

---

## Obsidian Integration

The evidence graph can eventually be exported as an Obsidian vault.

Example:

```text
data/obsidian/
│
├── papers/
│   ├── Paper A.md
│   └── Paper B.md
│
└── claims/
    ├── Claim A1.md
    └── Claim B1.md
```

A paper file could contain:

```markdown
# Paper A

## Claims

- [[Claim A1]]
- [[Claim A2]]

## Related Papers

- [[Paper B]]
- [[Paper C]]
```

Opening the generated directory as an Obsidian vault makes it possible to explore relationships through Obsidian's graph view.

---

## Research Direction

Scientific Evidence Graph is designed not only as an application, but also as a platform for experiments in scientific information retrieval.

Potential research questions include:

> Does claim-level retrieval identify relevant scientific literature better than abstract-level retrieval?

> Can language models reliably classify support, contradiction, and extension relationships between scientific claims?

> Does preserving the structure of scientific documents improve claim extraction?

> Can evidence graphs improve scientific literature exploration compared with conventional semantic search?

> Which embedding models perform best for claim-level scientific retrieval?

The modular architecture allows individual components to be replaced and benchmarked independently.

For example:

```text
Abstract Retrieval
        vs
Paragraph Retrieval
        vs
Claim Retrieval
```

or:

```text
Embedding Model A
        vs
Embedding Model B
```

or:

```text
Relationship Classifier A
        vs
Relationship Classifier B
```

Experimental development is described in more detail in [`ROADMAP.md`](ROADMAP.md).

---

## Technology

The project is primarily built in Python.

Core and planned technologies include:

```text
Python
├── PyMuPDF
├── Pydantic
├── httpx
├── sentence-transformers
├── FAISS
└── NetworkX
```

A future web interface may use:

```text
FastAPI
+
React
```

Technologies are introduced only when they solve a specific requirement of the system.

---

## Design Principles

### Modular Pipeline

Each stage should be independently replaceable.

```text
Parsing
 ↓
Extraction
 ↓
Retrieval
 ↓
Classification
 ↓
Graph
```

This makes experimentation and benchmarking easier.

### Preserve Sources

Generated claims and relationships should remain traceable to their original paper, page, section, and paragraph whenever possible.

### Structured Outputs

Components should exchange structured data rather than free-form responses whenever possible.

### Evidence Before Generation

The system should preserve and expose the evidence used to create relationships rather than generating unsupported connections.

---

## License

License to be determined.