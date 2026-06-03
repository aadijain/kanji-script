"""CLI entry point: argparse dispatch only.

The CLI is frontend-thin: it builds the parser, lets every feature register its
own subcommand (via jp_tools.services.register_all), and dispatches. Feature
logic lives in jp_tools.core / jp_tools.services. Adding a feature needs no edits
here - see jp_tools.services for the discovery mechanism.
"""

import argparse

from jp_tools.config import Settings
from jp_tools.services import register_all


def main() -> None:
    settings = Settings()
    parser = argparse.ArgumentParser(
        prog="jp-tools", description="Japanese-English study utilities."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    register_all(sub, settings)

    args = parser.parse_args()
    args.func(args, settings)


if __name__ == "__main__":
    main()
