from jp_tools.core.tokenization import get_pos_label, root_reading


def test_root_reading_and_cache():
    assert root_reading("行く") == "いく"
    assert root_reading("行く") == root_reading("行く")  # cached, same result


def test_get_pos_label():
    assert get_pos_label(("名詞", "普通名詞", "")) == "noun"
    assert get_pos_label(("名詞", "固有名詞", "地名")) == "proper noun"
    assert get_pos_label(("動詞", "", "")) == "verb"
    assert get_pos_label(("形容詞", "", "")) == "adjective"
    assert get_pos_label(("形状詞", "", "")) == "adjective"
    assert get_pos_label(()) == ""
