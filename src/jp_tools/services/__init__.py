"""Feature services: each subpackage is one self-contained functionality.

A feature composes the shared `jp_tools.core` toolbox and exposes a frontend-
agnostic entry point. It plugs into the CLI automatically by providing a `cli`
module with a `register_cli(subparsers, settings)` function - adding a feature is
just dropping in a new subpackage; no edits to the CLI adapter are needed.
"""

import importlib
import importlib.util
import pkgutil
from types import ModuleType
from typing import Iterator


def iter_feature_cli_modules() -> Iterator[ModuleType]:
    """Yield each feature subpackage's `cli` module that defines `register_cli`."""
    for info in pkgutil.iter_modules(__path__):
        if not info.ispkg:
            continue
        modname = f"{__name__}.{info.name}.cli"
        if importlib.util.find_spec(modname) is None:
            continue
        cli = importlib.import_module(modname)
        if hasattr(cli, "register_cli"):
            yield cli


def register_all(subparsers, settings) -> None:
    """Register every discovered feature's CLI subcommand on `subparsers`."""
    for cli in iter_feature_cli_modules():
        cli.register_cli(subparsers, settings)
