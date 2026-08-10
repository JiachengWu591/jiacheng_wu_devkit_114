# -*- coding: utf-8 -*-
"""
Shared CLI utilities: error handling decorator, output helpers, confirmation.
"""

from functools import wraps
from pathlib import Path
from typing import Callable, Iterator, Optional

import click
import typer
from rich.console import Console

from ..core.errors import DevkitError

console = Console()
err_console = Console(stderr=True)


def iter_leaf_commands(
    group: click.Group, prefix: tuple[str, ...] = ()
) -> Iterator[tuple[tuple[str, ...], click.Command]]:
    """
    Recursively walk a Click command tree, yielding (path, command) for every leaf
    (non-group) command, sorted by name at each level. `path` is the sequence of
    subcommand names leading to it, e.g. ("batch", "rename").

    Checks for a populated `.commands` mapping rather than `isinstance(cmd, click.Group)`:
    Typer's TyperGroup can fail that isinstance check depending on how click ends up
    imported, even though it behaves like a Group (has a `.commands` dict) at runtime.
    """
    for name, cmd in sorted(group.commands.items()):
        path = prefix + (name,)
        sub_commands = getattr(cmd, "commands", None)
        if sub_commands:
            yield from iter_leaf_commands(cmd, path)
        else:
            yield path, cmd


def format_usage(path: str, cmd: click.Command) -> str:
    """
    Build a copy-paste-style usage signature for a leaf command, e.g.
    "devkit convert data input --to <json|yaml|csv> [--output/-o output] [--flatten]".

    Every command's positional argument is shown as the generic placeholder "input", and any
    --output/-o option is shown with the value placeholder "output"—rather than each
    command's own differently-named metavar (input_file, logfile, src_dir, pattern, <path>,
    ...). This keeps every row `devkit help` prints using the same placeholder convention, so
    the table reads consistently across all commands. Every other option keeps its own
    Click-derived metavar (e.g. <json|yaml|csv>, <int>) so real constraints (choices, formats)
    stay visible.

    Positional arguments vs. options are told apart by whether a parameter's first `opts`
    entry starts with "-", not by isinstance(param, click.Argument): that check can fail for
    Typer-built commands depending on how click ends up imported (see iter_leaf_commands).
    """
    ctx = click.Context(cmd)
    parts = [path]
    for param in cmd.params:
        opts = list(getattr(param, "opts", []))
        is_option = bool(opts) and opts[0].startswith("-")
        if not is_option:
            parts.append("input" if param.required else "[input]")
            continue

        flags = "/".join(opts)
        if getattr(param, "is_flag", False):
            parts.append(f"[{flags}]")
            continue

        value = "output" if any(opt in ("--output", "-o") for opt in opts) else param.make_metavar(ctx=ctx)
        token = f"{flags} {value}" if param.required else f"[{flags} {value}]"
        if getattr(param, "multiple", False):
            token += "..."
        parts.append(token)
    return " ".join(parts)


def catch_devkit_errors(func: Callable) -> Callable:
    """
    Decorator: catch DevkitError from the wrapped function, print it in red, and exit with code 1.
    Other exceptions (bugs) pass through untouched, showing full traceback.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DevkitError as e:
            err_console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(code=1)

    return wrapper


def output_text(text: str, output_path: Optional[Path] = None) -> None:
    """
    Write text to file if output_path is given, otherwise print to stdout.
    """
    if output_path:
        output_path.write_text(text, encoding="utf-8")
        console.print(f"[green]Written to {output_path}[/green]")
    else:
        console.print(text)
