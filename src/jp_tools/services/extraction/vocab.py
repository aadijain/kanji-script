"""Vocabulary extraction, filtering, and sorting over tokenized text."""

import sys

from jp_tools.core.freq import FreqData, lookup_freq
from jp_tools.core.text import contains_kanji, contains_number, to_hiragana
from jp_tools.core.tokenization import (
    SPLIT_MODE,
    get_pos_label,
    root_reading,
    tokenizer_obj,
)

from .models import VocabEntry

# Valid sort keys. "none" preserves first-occurrence (input scan) order.
SORT_KEYS = ("none", "freq", "word", "reading", "pos")

# Entries with no freq_rank sort after all ranked entries (ascending order).
_NO_FREQ = float("inf")


def extract_vocab_entries(
    texts: list[str],
    deduplicate: bool = True,
    freq_data: FreqData | None = None,
) -> list[VocabEntry]:
    """Tokenize texts and build one VocabEntry per kanji-containing word.

    With deduplicate=True, only the first occurrence of each root form is kept.
    """
    seen_roots: set[str] = set()
    results: list[VocabEntry] = []

    for text in texts:
        try:
            tokens = tokenizer_obj.tokenize(text, SPLIT_MODE)
        except Exception as e:
            print(f"[warning] Tokenization failed for text segment: {e}", file=sys.stderr)
            continue
        for token in tokens:
            surface = token.surface()
            if not contains_kanji(surface) or contains_number(surface):
                continue
            root = token.dictionary_form()
            if deduplicate:
                if root in seen_roots:
                    continue
                seen_roots.add(root)
            freq_rank = (
                lookup_freq(freq_data, root, root_reading(root))
                if freq_data
                else None
            )
            results.append(VocabEntry(
                word=surface,
                root_form=root,
                reading=to_hiragana(token.reading_form()),
                pos=get_pos_label(token.part_of_speech()),
                freq_rank=freq_rank,
                example=text,
            ))

    return results


def filter_entries(
    entries: list[VocabEntry],
    min_freq_rank: int | None = None,
    max_freq_rank: int | None = None,
    pos_filter: set[str] | None = None,
) -> list[VocabEntry]:
    """Keep entries matching the freq-rank window and POS whitelist.

    A freq-rank filter excludes entries with no rank (freq_rank is None).
    """
    has_freq_filter = min_freq_rank is not None or max_freq_rank is not None
    filtered = []
    for entry in entries:
        if has_freq_filter and entry.freq_rank is None:
            continue
        if min_freq_rank is not None and entry.freq_rank < min_freq_rank:
            continue
        if max_freq_rank is not None and entry.freq_rank > max_freq_rank:
            continue
        if pos_filter is not None and entry.pos not in pos_filter:
            continue
        filtered.append(entry)
    return filtered


def _freq_key(entry: VocabEntry) -> float:
    return entry.freq_rank if entry.freq_rank is not None else _NO_FREQ


def sort_entries(
    entries: list[VocabEntry],
    sort_by: str = "none",
    reverse: bool = False,
) -> list[VocabEntry]:
    """Return entries sorted by the given key.

    - "none": keep first-occurrence order (no sorting)
    - "freq": by freq_rank ascending (most common first); unranked words go last
    - "word"/"reading"/"pos": alphabetical by that field

    Sorting is stable, so ties keep their original first-occurrence order.
    """
    if sort_by == "none":
        return list(entries)

    if sort_by == "freq":
        key = _freq_key
    elif sort_by in ("word", "reading", "pos"):
        key = lambda e: getattr(e, sort_by)
    else:
        raise ValueError(
            f"invalid sort key: {sort_by!r}; valid keys are {', '.join(SORT_KEYS)}"
        )

    return sorted(entries, key=key, reverse=reverse)
