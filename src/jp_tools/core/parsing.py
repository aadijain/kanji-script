"""Input file parsers for csv, txt, srt, ass/ssa.

The per-format readers take a Path and return text segments; they are reusable
by any adapter that has files on disk. Scanning a directory is a CLI concern.
"""

import csv
import re
import sys
from pathlib import Path

_SRT_TIMECODE = re.compile(r"^\d+:\d+:\d+[,\.]\d+\s*-->\s*\d+:\d+:\d+[,\.]\d+")
_SRT_INDEX = re.compile(r"^\d+$")
_HTML_TAG = re.compile(r"<[^>]+>")
_ASS_OVERRIDE = re.compile(r"\{[^}]*\}")


def extract_texts_from_csv(path: Path) -> list[str]:
    texts = []
    try:
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                for cell in row:
                    text = cell.strip()
                    if text:
                        texts.append(text)
    except Exception as e:
        print(f"[warning] Could not read {path}: {e}", file=sys.stderr)
    return texts


def extract_texts_from_txt(path: Path) -> list[str]:
    texts = []
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                text = line.strip()
                if text:
                    texts.append(text)
    except Exception as e:
        print(f"[warning] Could not read {path}: {e}", file=sys.stderr)
    return texts


def extract_texts_from_srt(path: Path) -> list[str]:
    texts = []
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or _SRT_INDEX.match(line) or _SRT_TIMECODE.match(line):
                    continue
                text = _HTML_TAG.sub("", line).strip()
                if text:
                    texts.append(text)
    except Exception as e:
        print(f"[warning] Could not read {path}: {e}", file=sys.stderr)
    return texts


def extract_texts_from_ass(path: Path) -> list[str]:
    texts = []
    try:
        # utf-8-sig: handles optional BOM in Windows-created ASS files
        with path.open(encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("Dialogue:"):
                    continue
                # Format: Dialogue: Layer, Start, End, Style, Name, MarginL, MarginR,
                #         MarginV, Effect, Text  (text is the 10th field, index 9)
                parts = line.split(",", 9)
                if len(parts) < 10:
                    continue
                text = _ASS_OVERRIDE.sub("", parts[9]).strip()
                if text:
                    texts.append(text)
    except Exception as e:
        print(f"[warning] Could not read {path}: {e}", file=sys.stderr)
    return texts


_PARSERS = {
    ".csv": extract_texts_from_csv,
    ".txt": extract_texts_from_txt,
    ".srt": extract_texts_from_srt,
    ".ass": extract_texts_from_ass,
    ".ssa": extract_texts_from_ass,
}


def parse_input_dir(input_dir: Path) -> list[str]:
    """Read every supported file in a directory into a flat list of text segments."""
    all_texts: list[str] = []
    for path in sorted(input_dir.iterdir()):
        parser = _PARSERS.get(path.suffix.lower())
        if parser:
            print(f"  Reading {path.name}...")
            all_texts.extend(parser(path))
    return all_texts
