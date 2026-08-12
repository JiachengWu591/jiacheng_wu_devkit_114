# -*- coding: utf-8 -*-
"""
`devkit log` command group: filter and summarize log files.
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer

from ..core.log import compile_log_pattern, compute_stats, filter_entries, parse_log_lines
from ._common import catch_devkit_errors, console, output_text

app = typer.Typer(help="Filter and summarize log files.")


class GroupBy(str, Enum):
    level = "level"


def _read_entries(logfile: Path, pattern: Optional[str]):
    compiled = compile_log_pattern(pattern)
    text = logfile.read_text(encoding="utf-8-sig")
    return parse_log_lines(text.splitlines(), pattern=compiled)


@app.command("filter")
@catch_devkit_errors
def filter_cmd(
    logfile: Annotated[Path, typer.Argument(exists=True, dir_okay=False, help="Path to the log file.")],
    level: Annotated[
        list[str],
        typer.Option("--level", help="Only include this level; repeatable (--level ERROR --level CRITICAL). Default: all levels."),
    ] = [],
    keyword: Annotated[
        Optional[str],
        typer.Option(
            "--keyword",
            help="Case-insensitive substring match against the full entry text (including multi-line tracebacks).",
        ),
    ] = None,
    since: Annotated[
        Optional[datetime],
        typer.Option(
            "--since",
            formats=["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"],
            help="Only entries at/after this time. Format: YYYY-MM-DD[ HH:MM:SS].",
        ),
    ] = None,
    until: Annotated[
        Optional[datetime],
        typer.Option(
            "--until",
            formats=["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"],
            help="Only entries at/before this time. Format: YYYY-MM-DD[ HH:MM:SS].",
        ),
    ] = None,
    pattern: Annotated[
        Optional[str],
        typer.Option(
            "--pattern",
            help="Custom regex overriding the built-in log-line pattern. Must define named groups: timestamp, level, message.",
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write filtered entries here instead of printing to stdout."),
    ] = None,
) -> None:
    """
    Filter a log file by level, keyword, and/or time range.

    Default log-line format: "YYYY-MM-DD[ T]HH:MM:SS[.,ms] LEVEL message". Lines that don't
    match (e.g. traceback continuation lines) are kept attached to the preceding entry, not
    dropped. All given filters combine with AND semantics.

    Examples:

        devkit log filter app.log --level ERROR --level CRITICAL

        devkit log filter app.log --keyword timeout --since "2026-08-07 10:00:00"
    """
    entries = _read_entries(logfile, pattern)
    filtered = filter_entries(entries, levels=level or None, keyword=keyword, since=since, until=until)
    output_text("\n".join(e.raw for e in filtered), output)


@app.command("stats")
@catch_devkit_errors
def stats_cmd(
    logfile: Annotated[Path, typer.Argument(exists=True, dir_okay=False, help="Path to the log file.")],
    group_by: Annotated[
        GroupBy,
        typer.Option("--group-by", help="How to group the summary."),
    ] = GroupBy.level,
    top_n: Annotated[
        int,
        typer.Option("--top-n", help="How many most-frequent messages to show per level."),
    ] = 10,
    pattern: Annotated[
        Optional[str],
        typer.Option(
            "--pattern",
            help="Custom regex overriding the built-in log-line pattern. Must define named groups: timestamp, level, message.",
        ),
    ] = None,
    as_json: Annotated[
        bool,
        typer.Option("--json", help="Emit machine-readable JSON instead of a human-readable summary. Recommended for scripts/AI agents."),
    ] = False,
) -> None:
    """
    Summarize a log file: counts per level, and the most frequent messages per level.

    Examples:

        devkit log stats app.log

        devkit log stats app.log --top-n 5 --json
    """
    entries = _read_entries(logfile, pattern)
    stats = compute_stats(entries, group_by=group_by.value, top_n=top_n)

    if as_json:
        # Plain print(), not console.print_json(): --json is documented as machine-readable
        # output for scripts/AI agents, and Rich's print_json() applies JSON syntax
        # highlighting whenever it detects color support—which some environments force on
        # even for redirected/piped output, silently corrupting the JSON with ANSI codes.
        print(json.dumps(stats))
        return

    for level_name, count in sorted(stats["level_counts"].items()):
        console.print(f"{level_name}: {count}")
    for level_name, messages in stats["top_messages"].items():
        if not messages:
            continue
        console.print(f"\n[bold]Top messages for {level_name}:[/bold]")
        for message, count in messages:
            console.print(f"  {count:>5}  {message}")
