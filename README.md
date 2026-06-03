# jp-tools

A collection of Japanese-English study utilities.

The project is structured as a reusable **core** library with thin **adapters** (CLI today; an HTTP service and Anki integration are planned), so the same logic can be driven from the command line, an API, or Anki.

## Disclaimer

- Personal hobby project, may not be actively maintained
- Cross-platform (Python 3.12), tested primarily on Ubuntu
- Developed with AI assistance (Claude)
- MIT licensed

## Setup

Uses [uv](https://docs.astral.sh/uv/) for dependency and environment management.

```bash
uv sync            # create the venv and install dependencies
```

## Tests

```bash
uv run pytest
```

## Project layout

```
src/jp_tools/
  core/                 Shared, feature-agnostic toolbox (no filesystem/argv/HTTP)
    text.py             Kanji/number character predicates, katakana -> hiragana
    parsing.py          Input file readers (csv, txt, srt, ass/ssa)
    tokenization.py     Sudachi setup, readings, POS labels
    freq.py             JPDB freq dictionary loading and lookup
  services/             One self-contained feature per subpackage, built on core
    extraction/         Feature: kanji vocab -> CSV (the first functionality)
      models.py         Pydantic VocabEntry
      vocab.py          Extraction, filtering, sorting over tokenized text
      service.py        extract_vocab(): frontend-agnostic extract -> filter -> sort
      csv_output.py     CSV serialization for the CLI frontend
      cli.py            register_cli(): self-registers the `extract` subcommand
  adapters/
    cli/                Command-line frontend (main.py: discovers + dispatches features)
    server/             HTTP service frontend (planned)
    anki/               Anki integration (planned)
  config.py             Settings via pydantic-settings
tests/                  pytest suite
```

Each feature is a self-contained subpackage under `services/` that composes the
shared `core/` toolbox. To add a feature, drop in `services/<feature>/` with a
`cli.py` exposing `register_cli(subparsers, settings)`; the CLI discovers it
automatically (no edits to `adapters/cli/main.py`). Keep the frontend-agnostic
pipeline in the feature's `service.py` so a future server/Anki adapter can reuse it.
