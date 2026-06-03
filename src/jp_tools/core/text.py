"""Character-level predicates and kana conversion."""

_JP_NUMERALS = frozenset("〇零一二三四五六七八九十百千万億兆")


def contains_number(word: str) -> bool:
    return any(c.isdigit() or "０" <= c <= "９" or c in _JP_NUMERALS for c in word)


def contains_kanji(word: str) -> bool:
    # 0x4E00–0x9FFF: CJK Unified Ideographs
    # 0x3400–0x4DBF: CJK Extension B
    # 0x20000–0x2A6DF: CJK Extension C
    # 0xF900–0xFAFF: CJK Compatibility Ideographs
    for ch in word:
        codepoint = ord(ch)
        if (
            0x4E00 <= codepoint <= 0x9FFF
            or 0x3400 <= codepoint <= 0x4DBF
            or 0x20000 <= codepoint <= 0x2A6DF
            or 0xF900 <= codepoint <= 0xFAFF
        ):
            return True
    return False


def to_hiragana(text: str) -> str:
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ン" else c for c in text)
