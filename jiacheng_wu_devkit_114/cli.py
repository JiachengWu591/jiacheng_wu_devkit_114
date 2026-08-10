# -*- coding: utf-8 -*-
"""
Main CLI entry point: assemble sub-command groups.

This file is intentionally thin—all business logic lives in core/ modules.
"""

from typing import Annotated, Optional

import typer

from .commands import batch as batch_commands
from .commands import convert as convert_commands
from .commands import log as log_commands
from .commands._common import console, format_usage, iter_leaf_commands
from .core.help import CommandEntry, search_entries

app = typer.Typer(
    help="devkit: universal CLI toolkit for data conversion, batch file ops, and log analysis.",
    epilog="Not sure which command you need? Run 'devkit help <keyword>', e.g. 'devkit help rename'.",
)

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


@app.command("help")
def help_cmd(
    keyword: Annotated[
        Optional[str],
        typer.Argument(
            help=(
                "Search every devkit command by keyword, matching against the command name and "
                "its help text (e.g. 'rename', 'csv', 'traceback'). Omit to list every command."
            ),
        ),
    ] = None,
) -> None:
    """
    Look up devkit commands by keyword, or list every command if no keyword is given.

    Searches across all command groups at once, so you don't need to know a command's group
    (convert/batch/log) to find it—e.g. 'devkit help csv' finds 'devkit convert data' even
    though 'csv' never appears in the group name.

    Examples:

        devkit help

        devkit help rename

        devkit help csv
    """
    root = typer.main.get_command(app)
    entries = [
        CommandEntry(
            path=(path_str := "devkit " + " ".join(path)),
            usage=format_usage(path_str, cmd),
            detail=cmd.help or "",
        )
        for path, cmd in iter_leaf_commands(root)
        if path != ("help",)
    ]

    matches = search_entries(entries, keyword)
    if not matches:
        console.print(f"[yellow]No commands matched {keyword!r}.[/yellow] Try [bold]devkit --help[/bold] to browse everything.")
        return

    for entry in matches:
        console.print(entry.usage)


def main() -> None:
    # windows_expand_args=False: by default Click auto-expands glob-looking arguments
    # (e.g. "*.jpg") on Windows to compensate for cmd.exe/PowerShell not globbing natively.
    # `devkit batch` commands need the raw pattern string themselves (core.batch.expand_glob
    # implements ** recursion consistently across platforms), so that auto-expansion must
    # stay off—otherwise Windows callers get "unexpected extra argument(s)" errors.
    app(windows_expand_args=False)


if __name__ == "__main__":
    main()
