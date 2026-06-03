"""Pydantic models for the extraction feature (the data each adapter serializes)."""

from pydantic import BaseModel


class VocabEntry(BaseModel):
    """A vocabulary item extracted from text, with metadata.

    `freq_rank` is None when no frequency data was available (serializes to an
    empty CSV cell and to JSON null).
    """

    word: str          # first surface form seen for this root
    root_form: str     # Sudachi dictionary form (SplitMode.A)
    reading: str       # pronunciation in hiragana
    pos: str           # English part-of-speech label
    freq_rank: int | None = None  # JPDB global rank; lower = more common
    example: str       # source text where the word was first seen
