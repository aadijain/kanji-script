from jp_tools.core.text import contains_kanji, contains_number


def test_contains_kanji():
    assert contains_kanji("東京")
    assert contains_kanji("行った")
    assert not contains_kanji("ひらがな")
    assert not contains_kanji("hello")


def test_contains_number():
    assert contains_number("3月")
    assert contains_number("３月")
    assert contains_number("一月")
    assert contains_number("三十五")
    assert not contains_number("東京")
