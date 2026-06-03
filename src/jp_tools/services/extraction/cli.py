"""CLI binding for the extraction feature.

`register_cli` is auto-discovered by `jp_tools.services.register_all`, so this
feature plugs into the `jp-tools` CLI without any edits to the CLI adapter.
The frontend-agnostic pipeline lives in `service.py`; this module only does the
CLI-specific work (argument parsing, file IO, CSV output).
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from jp_tools.config import Settings
from jp_tools.core.freq import load_freq_dict
from jp_tools.core.parsing import parse_input_dir

from .csv_output import DEFAULT_COLUMNS, write_csv
from .service import extract_vocab
from .vocab import SORT_KEYS


def register_cli(sub: argparse._SubParsersAction, settings: Settings) -> None:
    p = sub.add_parser(
        "extract", help="Extract unique kanji vocabulary from input files."
    )
    p.add_argument(
        "--input-dir", default=str(settings.input_dir), metavar="DIR",
        help=f"Directory containing input files (default: {settings.input_dir})",
    )
    p.add_argument(
        "--output", default=settings.output, metavar="FILE",
        help=f"Output filename stem (default: {settings.output}, "
             f"written to {settings.output_dir}/<stem>_<timestamp>.csv)",
    )
    p.add_argument(
        "--no-dedup", action="store_true",
        help="Include all occurrences instead of deduplicating by root form",
    )
    p.add_argument(
        "--freq-dict", default=None, metavar="ZIP",
        help=f"Path to JPDB freq list zip (default: {settings.freq_dict})",
    )
    p.add_argument(
        "--min-freq-rank", type=int, default=None, metavar="N",
        help="Only include words with frequency rank >= N (less common words)",
    )
    p.add_argument(
        "--max-freq-rank", type=int, default=None, metavar="N",
        help="Only include words with frequency rank <= N (more common words)",
    )
    p.add_argument(
        "--pos", default=None, metavar="POS1,POS2,...",
        help="Only include these parts of speech (comma-separated, e.g. 'noun,verb')",
    )
    p.add_argument(
        "--columns", default=None, metavar="COL1,COL2,...",
        help="Only include these columns (comma-separated, e.g. 'word,reading,pos')",
    )
    p.add_argument(
        "--sort", default="none", choices=SORT_KEYS, metavar="KEY",
        help=f"Sort output rows by KEY ({', '.join(SORT_KEYS)}); "
             "default 'none' keeps first-occurrence order",
    )
    p.add_argument(
        "--reverse", action="store_true",
        help="Reverse the sort order (only meaningful with --sort)",
    )
    p.set_defaults(func=run)


def run(args: argparse.Namespace, settings: Settings) -> None:
    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        print(f"Error: input directory '{input_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    # Resolve freq dict: explicit --freq-dict must exist; default may be absent.
    freq_data = None
    freq_path = Path(args.freq_dict) if args.freq_dict else settings.freq_dict
    if args.freq_dict and not freq_path.exists():
        print(f"Error: freq dict '{freq_path}' not found.", file=sys.stderr)
        sys.exit(1)
    elif freq_path.exists():
        print(f"Loading freq dict from {freq_path}...")
        freq_data = load_freq_dict(freq_path)
    else:
        print(f"[info] Freq dict not found at {freq_path}, skipping freq_rank.", file=sys.stderr)

    columns = None
    if args.columns:
        columns = [c.strip() for c in args.columns.split(",")]
        invalid = set(columns) - set(DEFAULT_COLUMNS)
        if invalid:
            print(
                f"Error: invalid columns: {', '.join(invalid)}. Valid columns are: "
                f"{', '.join(DEFAULT_COLUMNS)}",
                file=sys.stderr,
            )
            sys.exit(1)

    print(f"Scanning {input_dir}/...")
    texts = parse_input_dir(input_dir)
    print(f"Extracted {len(texts)} text segments. Running Sudachi...")

    pos_filter = {p.strip() for p in args.pos.split(",")} if args.pos else None
    entries = extract_vocab(
        texts,
        deduplicate=not args.no_dedup,
        freq_data=freq_data,
        min_freq_rank=args.min_freq_rank,
        max_freq_rank=args.max_freq_rank,
        pos_filter=pos_filter,
        sort_by=args.sort,
        reverse=args.reverse,
    )

    settings.output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = Path(args.output)
    suffix = stem.suffix or ".csv"
    output_path = settings.output_dir / f"{stem.stem}_{timestamp}{suffix}"

    write_csv(entries, output_path, columns=columns)
    print(f"Done. {len(entries)} unique kanji words written to '{output_path}'.")
