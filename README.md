# kanji-script

Extract unique kanji vocabulary from Japanese text sources — Anki exports, subtitle files, word lists — and output a clean CSV for study.

## Usage

```bash
source venv/bin/activate
python extract_kanji.py
# reads all files in input/, writes kanji.csv
```

Options:
```
--input-dir DIR   Source directory (default: input/)
--output FILE     Output CSV path (default: kanji.csv)
```

## Input formats

Place any of the following in `input/`:

| Format | Notes |
|--------|-------|
| `.csv` | Cells may contain space-separated words or full sentences |
| `.txt` | One sentence or word per line |
| `.srt` | Subtitles — timecodes and sequence numbers stripped |
| `.ass` / `.ssa` | Subtitles — `Dialogue:` lines parsed, `{...}` override tags stripped |

## Output

`kanji.csv` with columns:

| Column | Description |
|--------|-------------|
| `word` | First surface form encountered |
| `root_form` | Sudachi dictionary form (conjugation variants collapse to one entry) |
| `tag` | `person`, `place`, or empty |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install pandas sudachipy sudachidict_core
```
