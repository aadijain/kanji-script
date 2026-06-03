"""Extraction feature: kanji vocabulary from Japanese text -> structured entries.

One self-contained functionality built on the shared `jp_tools.core` toolbox
(parsing, tokenization, freq, text). `service.extract_vocab` is the frontend-
agnostic entry point any adapter (CLI today, server later) can call.
"""

from .models import VocabEntry
from .service import extract_vocab

__all__ = ["VocabEntry", "extract_vocab"]
