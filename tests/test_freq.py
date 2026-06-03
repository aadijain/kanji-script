from jp_tools.core.freq import DEFAULT_FREQ_DICT, FreqData, load_freq_dict, lookup_freq
from jp_tools.services.extraction.vocab import extract_vocab_entries


def test_lookup_freq():
    freq_data: FreqData = ({("東京", "とうきょう"): 42}, {"東京": 42})
    assert lookup_freq(freq_data, "東京", "とうきょう") == 42
    assert lookup_freq(freq_data, "東京", "unknown") == 42  # falls back to by_term
    assert lookup_freq(freq_data, "大阪", "おおさか") is None


def test_extract_with_default_freq_dict():
    if not DEFAULT_FREQ_DICT.exists():
        import pytest
        pytest.skip("default freq dict not installed")
    fd = load_freq_dict(DEFAULT_FREQ_DICT)
    rows = extract_vocab_entries(["東京に行った"], freq_data=fd)
    by_root = {r.root_form: r for r in rows}
    assert isinstance(by_root["東京"].freq_rank, int)
