"""CSV serialization for extracted vocab (the CLI frontend's output format)."""

import csv
from pathlib import Path

from .models import VocabEntry

DEFAULT_COLUMNS = ["word", "root_form", "reading", "pos", "freq_rank", "example"]


def write_csv(
    entries: list[VocabEntry],
    output_path: Path,
    columns: list[str] | None = None,
) -> None:
    if columns is None:
        columns = DEFAULT_COLUMNS

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for entry in entries:
            data = entry.model_dump()
            # csv renders None (missing freq_rank) as an empty cell.
            writer.writerow({col: data.get(col) for col in columns})
