# Repository Guidelines

## Project Structure & Module Organization

SEG is a Python 3.11+ package using a `src` layout. Application code lives in
`src/evidence_graph/`. Keep functionality in the corresponding domain package:
`ingestion/` for PDF parsing, `retrieval/` for search and ranking, `extraction/`
for claims, `relations/` for stance classification, and `graph/` for graph
construction and export. Shared Pydantic models belong in `models/`, while
pipeline orchestration belongs in `pipeline/`. The CLI entry point is
`src/evidence_graph/main.py`.

Tests live in `tests/` and mirror behavior by module, for example
`tests/test_paper_search.py`. Runtime papers and generated artifacts belong
under `data/` and must not be committed. Consult `ROADMAP.md` before expanding
the project scope.

## Build, Test, and Development Commands

- `uv sync`: create or update the environment from `pyproject.toml`.
- `uv run pytest`: run the complete test suite.
- `uv run pytest tests/test_paper_search.py -q`: run one focused test module.
- `uv run seg paper.pdf --limit 5`: run the recommendation CLI.
- `uv run seg paper.pdf --from-year 2022 --open-access --json`: exercise filters
  and machine-readable output.
- `uv build`: build source and wheel distributions.

## Coding Style & Naming Conventions

Use four-space indentation and conventional PEP 8 naming: `snake_case` for
functions and modules, `PascalCase` for classes, and `UPPER_CASE` for constants.
Add type annotations to public APIs and prefer small, single-purpose functions.
Use `pathlib.Path` for filesystem paths and Pydantic models or dataclasses for
structured boundaries. Keep network and filesystem operations behind classes so
they can be tested independently. No formatter or linter is currently enforced;
match surrounding code and keep imports grouped as standard library, third-party,
then local modules.

## Testing Guidelines

Tests use `pytest` and follow `test_<behavior>` naming. Add tests for successful
behavior, validation failures, and external-response parsing. Mock network calls
in routine tests; do not require OpenAlex or API credentials for the suite. Every
bug fix should include a regression test. Run `uv run pytest` before submitting.

## Commit & Pull Request Guidelines

History generally follows Conventional Commit prefixes such as `feat:`,
`fix:`, `refactor:`, and `chore:`. Write imperative, focused subjects and avoid
mixing unrelated changes. Pull requests should explain the motivation, summarize
the implementation, list verification commands, and link relevant issues. Include
sample CLI output for user-visible changes and screenshots only when adding a TUI
or web interface. Never commit papers, API keys, or generated result data.
