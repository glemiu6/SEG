<div align="center">

# SEG

**Upload a research paper and discover relevant work.**

![SEG — Discover relevant research](docs/assets/readme_photo.png)

![status](https://img.shields.io/badge/status-prototype-orange)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

[Quickstart](#quickstart) · [How it works](#how-it-works) · [Examples](#common-workflows) · [CLI options](#cli-reference) · [Development](#development)

</div>

SEG is a command-line research-paper recommender. Give it a text-based PDF and
it returns related papers with publication metadata, research areas, summaries,
and links. Optional local models improve ranking and explain why each result is
relevant.

## What works today

- Extract a paper's title, authors, text, and abstract locally.
- Search scholarly metadata and abstracts through OpenAlex.
- Filter by venue, year range, and open-access status.
- Exclude the uploaded paper and collapse duplicate DOI/title versions.
- Rerank candidates with local Ollama embeddings.
- Generate structured summaries, areas, and relevance explanations locally.
- Cache searches, embeddings, and analyses in SQLite.
- Print readable terminal results or machine-readable JSON.

> [!NOTE]
> SEG is a research prototype. Image-only PDFs require OCR and are not yet
> supported. LLM output is based on abstracts and should not be treated as a
> substitute for reading the paper.

## Quickstart

Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/), and internet access
for OpenAlex.

```bash
git clone https://github.com/glemiu6/SEG.git
cd SEG
uv sync
uv run seg path/to/paper.pdf
```

That command uses OpenAlex ranking and extractive summaries. No local model is
required.

For the best current results, install [Ollama](https://ollama.com/), start it,
and download one embedding and one generation model:

```bash
ollama serve
ollama pull bge-m3
ollama pull qwen3:8b

uv run seg paper.pdf --rerank --llm
```

## How it works

```text
PDF
 └─ local extraction: title + abstract
       └─ search terms + filters
             └─ OpenAlex candidate papers
                   └─ remove source paper and duplicates
                         └─ optional local embedding rerank
                               └─ optional local LLM analysis
                                     └─ terminal output or JSON
```

The source abstract is preferred throughout the pipeline. If no abstract
heading is detected, SEG falls back to text from the first three pages.

### Data sent to each service

| Component | Receives | Purpose |
|---|---|---|
| OpenAlex | Search terms and objective filters | Find candidate papers and metadata |
| Embedding model | Source abstract and candidate abstracts, up to 12,000 characters each | Compute semantic similarity |
| Generation model | Source title/text, candidate title/abstract, and OpenAlex topics | Produce summary, areas, and relevance |

PDF files are never sent to OpenAlex or Ollama. Ollama is local by default at
`http://localhost:11434`.

## Common workflows

Filter by publication information:

```bash
uv run seg paper.pdf --venue NeurIPS --from-year 2022 --to-year 2026 --open-access
```

Rerank 50 candidates and return the best 10:

```bash
uv run seg paper.pdf --rerank --candidate-pool 50 --limit 10
```

Rerank first, then explain only the final results with a local LLM:

```bash
uv run seg paper.pdf --rerank --llm --model llama3.1:8b --limit 5
```

Produce JSON for another program or a future UI:

```bash
uv run seg paper.pdf --rerank --llm --json
```

Use a remote Ollama-compatible server without persistent caching:

```bash
uv run seg paper.pdf --rerank --llm \
  --ollama-url http://192.168.1.20:11434 --no-cache
```

## CLI reference

```text
uv run seg PAPER [OPTIONS]
```

| Argument | Default | Description |
|---|---:|---|
| `paper` | required | Path to a text-based PDF |
| `-h`, `--help` | — | Show command help |
| `--venue NAME` | any | Case-insensitive conference or journal substring |
| `--from-year YEAR` | any | Earliest publication year |
| `--to-year YEAR` | any | Latest publication year; cannot precede `--from-year` |
| `--open-access` | off | Return only OpenAlex open-access papers |
| `--limit N` | `5` | Final result count, from 1 to 50 |
| `--json` | off | Emit JSON instead of formatted terminal output |
| `--rerank` | off | Rerank candidates with local embeddings |
| `--embedding-model NAME` | `bge-m3` | Ollama model used by `--rerank` |
| `--candidate-pool N` | `30` | Reranking pool; must be between `--limit` and 100 |
| `--llm` | off | Generate summary, areas, and relevance with Ollama |
| `--model NAME` | `qwen3:8b` | Ollama generation model used by `--llm` |
| `--ollama-url URL` | `http://localhost:11434` | Ollama server used for both model types |
| `--cache-path PATH` | `data/cache/seg.sqlite3` | SQLite cache location |
| `--no-cache` | off | Disable persistent cache reads and writes |

Run `uv run seg --help` for the options installed with your version.

## Ranking and duplicate handling

OpenAlex initially ranks candidates by textual relevance. With `--rerank`, SEG
embeds the source and candidate abstracts in one local batch, calculates cosine
similarity, and orders results by that score. Candidates without abstracts are
placed after candidates that can be scored.

Before reranking, SEG removes:

- a result whose normalized title matches the uploaded paper;
- repeated DOI records, including URL and `doi:` forms; and
- repeated titles that differ only in capitalization or punctuation.

The earliest/highest-ranked version is retained. SEG requests a small candidate
buffer so duplicate removal is less likely to reduce the requested result count.

## Summaries and local LLMs

Without `--llm`, SEG displays up to two abstract sentences. With `--llm`, it
asks Ollama for validated JSON containing:

```json
{
  "summary": "What the candidate paper investigates.",
  "research_areas": ["Information retrieval", "Language models"],
  "relevance": "Why this paper is related to the uploaded paper."
}
```

Candidates without abstracts are not sent to the generation model. Model output
is validated with Pydantic before display.

## Cache

Caching is enabled by default at `data/cache/seg.sqlite3`:

| Data | Expiration |
|---|---|
| OpenAlex responses | 24 hours |
| Individual embedding vectors | No automatic expiration |
| LLM analyses | No automatic expiration |

Keys include the effective input and model configuration, so changing a model,
prompt, text, or filter produces a new entry. Failed requests are not cached.

```bash
uv run seg paper.pdf --cache-path /tmp/seg.sqlite3
uv run seg paper.pdf --no-cache
```

## Project structure

```text
src/evidence_graph/
├── ingestion/    # PDF and abstract extraction
├── retrieval/    # OpenAlex search, embeddings, ranking, deduplication
├── llm/          # Ollama client, prompts, schemas, summarization
├── storage/      # SQLite and JSON persistence
├── models/       # shared Pydantic schemas
├── extraction/   # planned claim extraction
├── relations/    # planned evidence classification
├── graph/        # planned evidence graph output
└── main.py       # CLI entry point
tests/            # pytest suite
```

## Development

```bash
uv sync                 # install project and development dependencies
uv run pytest           # run all tests
uv run pytest -q        # concise test output
uv build                # build wheel and source distributions
```

Routine tests mock external services; they do not require OpenAlex or Ollama.
See [AGENTS.md](AGENTS.md) for contributor conventions and
[ROADMAP.md](ROADMAP.md) for the longer-term evidence-graph research plan.

## Next milestones

1. Add OCR for scanned PDFs.
2. Export and reload recommendation sessions.
3. Build an interactive TUI over the same pipeline.
4. Evaluate recommendation quality on a small labeled paper set.
5. Extend retrieval from paper similarity to claim-level evidence.

## License

MIT. See [LICENSE](LICENSE).
