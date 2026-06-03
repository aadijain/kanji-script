from jp_tools.services.extraction.models import VocabEntry
from jp_tools.services.extraction.vocab import (
    extract_vocab_entries,
    filter_entries,
    sort_entries,
)


def test_numbers_are_filtered():
    roots = {r.root_form for r in extract_vocab_entries(["3月に行った"])}
    assert "3月" not in roots, "ascii-digit words should be filtered"
    roots_wide = {r.root_form for r in extract_vocab_entries(["３月に行った"])}
    assert "３月" not in roots_wide, "fullwidth-digit words should be filtered"


def test_extraction_basics():
    rows = extract_vocab_entries(["私は東京に行った"])
    assert len(rows) == 3
    by_root = {r.root_form: r for r in rows}
    assert by_root["行く"].pos == "verb"
    assert by_root["行く"].reading == "いっ"
    assert by_root["東京"].pos == "proper noun"
    assert all(r.example == "私は東京に行った" for r in rows)
    assert all(r.freq_rank is None for r in rows), "freq_rank is None without freq_data"


def test_dedup_off_keeps_repeats():
    rows = extract_vocab_entries(["行った", "行く"], deduplicate=False)
    roots = [r.root_form for r in rows]
    assert roots.count("行く") == 2


def _sample_entries() -> list[VocabEntry]:
    return [
        VocabEntry(word="東京", root_form="東京", reading="とうきょう", pos="proper noun", freq_rank=100, example=""),
        VocabEntry(word="行く", root_form="行く", reading="いく", pos="verb", freq_rank=500, example=""),
        VocabEntry(word="走る", root_form="走る", reading="はしる", pos="verb", freq_rank=1000, example=""),
        VocabEntry(word="赤", root_form="赤", reading="あか", pos="adjective", freq_rank=2000, example=""),
        VocabEntry(word="です", root_form="です", reading="です", pos="auxiliary verb", freq_rank=None, example=""),
    ]


def test_filter_max_freq():
    filtered = filter_entries(_sample_entries(), max_freq_rank=1000)
    assert len(filtered) == 3
    assert all(e.freq_rank is not None and e.freq_rank <= 1000 for e in filtered)


def test_filter_min_freq():
    filtered = filter_entries(_sample_entries(), min_freq_rank=500)
    assert len(filtered) == 3
    assert all(e.freq_rank is not None and e.freq_rank >= 500 for e in filtered)


def test_filter_pos():
    filtered = filter_entries(_sample_entries(), pos_filter={"verb"})
    assert len(filtered) == 2
    assert all(e.pos == "verb" for e in filtered)


def test_filter_combined():
    filtered = filter_entries(_sample_entries(), max_freq_rank=500, pos_filter={"verb"})
    assert len(filtered) == 1
    assert filtered[0].root_form == "行く"


def test_sort_none_preserves_order():
    entries = _sample_entries()
    assert sort_entries(entries, "none") == entries
    assert sort_entries(entries) == entries, "default is no sorting"


def test_sort_freq_unranked_last():
    by_freq = sort_entries(_sample_entries(), "freq")
    assert [e.root_form for e in by_freq] == ["東京", "行く", "走る", "赤", "です"]
    assert by_freq[-1].root_form == "です"


def test_sort_freq_reverse():
    by_freq_rev = sort_entries(_sample_entries(), "freq", reverse=True)
    assert [e.root_form for e in by_freq_rev] == ["です", "赤", "走る", "行く", "東京"]


def test_sort_reading_and_pos():
    entries = _sample_entries()
    by_reading = sort_entries(entries, "reading")
    assert [e.reading for e in by_reading] == sorted(e.reading for e in entries)
    by_pos = sort_entries(entries, "pos")
    assert [e.pos for e in by_pos] == sorted(e.pos for e in entries)


def test_sort_does_not_mutate_input():
    entries = _sample_entries()
    sort_entries(entries, "freq")
    assert entries[0].root_form == "東京", "sort_entries must not mutate input"
