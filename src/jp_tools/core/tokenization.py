"""Sudachi tokenizer setup and token-level helpers."""

import functools

from sudachipy import dictionary, tokenizer as sudachi_tokenizer

from .text import to_hiragana

# Sudachi tokenizer setup: SplitMode.A gives finest granularity,
# ensuring individual kanji are not masked in compound words.
tokenizer_obj = dictionary.Dictionary().create()
SPLIT_MODE = sudachi_tokenizer.Tokenizer.SplitMode.A


@functools.cache
def root_reading(root: str) -> str:
    """Return the canonical hiragana reading of a dictionary form.

    Cached because dictionary-form lookups repeat heavily across token batches.
    """
    try:
        tokens = tokenizer_obj.tokenize(root, SPLIT_MODE)
        return to_hiragana("".join(t.reading_form() for t in tokens))
    except Exception:
        return ""


_POS_MAP = {
    "動詞": "verb",
    "形容詞": "adjective",
    "形状詞": "adjective",
    "副詞": "adverb",
    "代名詞": "pronoun",
    "接続詞": "conjunction",
    "感動詞": "interjection",
    "助動詞": "auxiliary verb",
    "助詞": "particle",
    "接尾辞": "suffix",
    "接頭辞": "prefix",
    "連体詞": "pre-noun adjectival",
}


def get_pos_label(pos) -> str:
    if not pos:
        return ""
    main = pos[0]
    if main == "名詞":
        return "proper noun" if len(pos) > 1 and pos[1] == "固有名詞" else "noun"
    return _POS_MAP.get(main, main)
