from jp_tools.services.extraction.csv_output import write_csv
from jp_tools.services.extraction.models import VocabEntry

_ENTRIES = [
    VocabEntry(word="東京", root_form="東京", reading="とうきょう", pos="proper noun", freq_rank=100, example="東京に行った"),
    VocabEntry(word="行く", root_form="行く", reading="いく", pos="verb", freq_rank=None, example="東京に行った"),
]


def test_write_csv_subset_columns(tmp_path):
    out = tmp_path / "out.csv"
    write_csv(_ENTRIES, out, columns=["word", "pos", "freq_rank"])
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "word,pos,freq_rank"
    assert "東京" in lines[1] and "proper noun" in lines[1]
    assert len(lines) == 3, "header + 2 entries"


def test_write_csv_default_columns_and_none_renders_empty(tmp_path):
    out = tmp_path / "out.csv"
    write_csv(_ENTRIES, out)
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "word,root_form,reading,pos,freq_rank,example"
    # second entry has freq_rank=None -> empty cell, not "None"
    assert lines[2].split(",")[4] == ""
