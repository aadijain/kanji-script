"""Vocabulary extraction service: the reusable pipeline every adapter calls.

Takes already-acquired text segments (no filesystem/HTTP concerns) and returns
VocabEntry models, composing the core extract -> filter -> sort steps.
"""

from jp_tools.core.freq import FreqData

from .models import VocabEntry
from .vocab import extract_vocab_entries, filter_entries, sort_entries


def extract_vocab(
    texts: list[str],
    *,
    deduplicate: bool = True,
    freq_data: FreqData | None = None,
    min_freq_rank: int | None = None,
    max_freq_rank: int | None = None,
    pos_filter: set[str] | None = None,
    sort_by: str = "none",
    reverse: bool = False,
) -> list[VocabEntry]:
    entries = extract_vocab_entries(texts, deduplicate=deduplicate, freq_data=freq_data)
    entries = filter_entries(entries, min_freq_rank, max_freq_rank, pos_filter)
    entries = sort_entries(entries, sort_by, reverse)
    return entries
