# -*- coding: utf-8 -*-
"""
Main CLI entry point: assemble sub-command groups.

This file is intentionally thin—all business logic lives in core/ modules.
"""

import typer

from .commands import batch as batch_commands
from .commands import convert as convert_commands
from .commands import log as log_commands

app = typer.Typer(help="devkit: universal CLI toolkit for data conversion, batch file ops, and log analysis.")

app.add_typer(
    convert_commands.app,
    name="convert",
    help="Convert between JSON/YAML/CSV, and PDF to Markdown.",
)
app.add_typer(
    batch_commands.app,
    name="batch",
    help="Batch rename or organize files, with a preview + confirmation safety net.",
)
app.add_typer(
    log_commands.app,
    name="log",
    help="Filter and summarize log files.",
)


def main() -> None:
    # windows_expand_args=False: by default Click auto-expands glob-looking arguments
    # (e.g. "*.jpg") on Windows to compensate for cmd.exe/PowerShell not globbing natively.
    # `devkit batch` commands need the raw pattern string themselves (core.batch.expand_glob
    # implements ** recursion consistently across platforms), so that auto-expansion must
    # stay off—otherwise Windows callers get "unexpected extra argument(s)" errors.
    app(windows_expand_args=False)


if __name__ == "__main__":
    main()
