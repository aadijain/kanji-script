# jp-tools

A collection of Japanese-English study utilities. The first capability is extracting unique kanji vocabulary from Japanese text sources (Anki exports, subtitle files, word lists) into a clean CSV.

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

## Quick start

```bash
uv run jp-tools extract        # reads all files in input/, writes output/kanji_<timestamp>.csv
```

`jp-tools` is a subcommand-based CLI; `extract` is the first subcommand. Run `uv run jp-tools --help` or `uv run jp-tools extract --help` for usage.

## Input formats

Place any of the following in `input/`:

| Format | Notes |
|--------|-------|
| `.csv` | Cells may contain space-separated words or full sentences |
| `.txt` | One sentence or word per line |
| `.srt` | Subtitles: timecodes and sequence numbers stripped |
| `.ass` / `.ssa` | Subtitles: `Dialogue:` lines parsed, `{...}` override tags stripped |

## Output

Output files are written to `output/` with a timestamp appended (format: `<name>_<YYYYMMDD_HHMMSS>.csv`). Default filename stem is `kanji`.

By default, rows appear in first-occurrence order (the order words are first encountered while scanning the input). Use `--sort` to order them by frequency, word, reading, or part of speech.

| Column | Description |
|--------|-------------|
| `word` | First surface form encountered |
| `root_form` | Sudachi dictionary form (conjugation variants collapse to one entry) |
| `reading` | Pronunciation in hiragana |
| `pos` | Part of speech: `noun`, `verb`, `adjective`, `adverb`, etc. |
| `freq_rank` | JPDB global frequency rank (lower = more common); empty if dict not available |
| `example` | Source sentence where the word was first seen |

## `extract` options

```
--max-freq-rank N      Only words with frequency rank <= N (more common)
--min-freq-rank N      Only words with frequency rank >= N (less common)
--pos POS1,POS2,...    Only these parts of speech (comma-separated)
--columns COL1,COL2... Only these output columns
--sort KEY             Sort rows by KEY: none, freq, word, reading, pos (default: none)
--reverse              Reverse the sort order (only meaningful with --sort)
--input-dir DIR        Source directory (default: input/)
--output FILE          Output filename stem (default: kanji)
--no-dedup             Include all occurrences (default: first per root form only)
--freq-dict ZIP        Path to JPDB freq list zip (default: ~/.local/share/japanese-dicts/jpdb-freq-list.zip)
```

Examples:
```bash
# Only top 1000 most common words
uv run jp-tools extract --max-freq-rank 1000

# Only nouns and verbs
uv run jp-tools extract --pos noun,verb

# Words between rank 500 and 5000, only adjectives
uv run jp-tools extract --min-freq-rank 500 --max-freq-rank 5000 --pos adjective

# Only show word, reading, and frequency rank
uv run jp-tools extract --columns word,reading,freq_rank

# Sort by frequency, most common first (unranked words go last)
uv run jp-tools extract --sort freq

# Sort by frequency, least common first
uv run jp-tools extract --sort freq --reverse
```

Possible `--sort` values: `none` (first-occurrence, default), `freq`, `word`, `reading`, `pos`.

Possible `--pos` values:
```
noun, proper noun, verb, adjective, adverb, pronoun, conjunction, interjection,
auxiliary verb, particle, suffix, prefix, pre-noun adjectival
```

Possible `--columns` values: `word, root_form, reading, pos, freq_rank, example`.

## Configuration

Defaults can be overridden with environment variables (prefix `JP_TOOLS_`) or a local `.env` file. CLI flags take precedence over both.

```bash
JP_TOOLS_INPUT_DIR=mydir JP_TOOLS_OUTPUT=mywords uv run jp-tools extract
```

Available settings: `JP_TOOLS_INPUT_DIR`, `JP_TOOLS_OUTPUT_DIR`, `JP_TOOLS_OUTPUT`, `JP_TOOLS_FREQ_DICT`.

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

## How it works

The pipeline automatically sanitizes input and extracts kanji vocabulary:

- **Whitespace:** Strips leading/trailing whitespace from all input lines and cells
- **SRT files:** Removes sequence numbers, timecodes, and HTML tags like `<b>` or `<i>`
- **ASS/SSA files:** Extracts only `Dialogue:` lines; removes `{...}` override tags (styling, karaoke timing, etc.)
- **Word filtering:** Removes words containing numbers (ASCII 0-9, fullwidth ０-９, Japanese numerals 〇-兆); removes words with no kanji
- **Reading conversion:** Converts all katakana readings to hiragana for consistency
- **Deduplication:** By default, only the first occurrence of each root form is kept (use `--no-dedup` to include all)
