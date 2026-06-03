"""JPDB frequency dictionary loading and lookup."""

import json
import zipfile
from pathlib import Path

# Python 3.12+: type alias for frequency data (by_reading, by_term)
type FreqData = tuple[dict[tuple[str, str], int], dict[str, int]]

DEFAULT_FREQ_DICT = Path("~/.local/share/japanese-dicts/jpdb-freq-list.zip").expanduser()


def load_freq_dict(path: Path) -> FreqData:
    """Load JPDB freq list zip. Returns (by_reading, by_term) rank dicts."""
    by_reading: dict[tuple[str, str], int] = {}
    by_term: dict[str, int] = {}
    with zipfile.ZipFile(path) as zf:
        with zf.open("term_meta_bank_1.json") as fh:
            data = json.load(fh)
    for entry in data:
        if len(entry) < 3 or entry[1] != "freq":
            continue
        term, meta = entry[0], entry[2]
        if not isinstance(meta, dict):
            continue
        if "frequency" in meta:
            rank = meta["frequency"].get("value")
            reading = meta.get("reading")
        else:
            rank = meta.get("value")
            reading = None
        if not isinstance(rank, int):
            continue
        if reading:
            key = (term, reading)
            if key not in by_reading or rank < by_reading[key]:
                by_reading[key] = rank
        if term not in by_term or rank < by_term[term]:
            by_term[term] = rank
    return by_reading, by_term


def lookup_freq(
    freq_data: FreqData,
    root_form: str,
    reading: str,
) -> int | None:
    by_reading, by_term = freq_data
    return by_reading.get((root_form, reading)) or by_term.get(root_form)
