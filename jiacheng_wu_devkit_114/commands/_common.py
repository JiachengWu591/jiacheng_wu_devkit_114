# -*- coding: utf-8 -*-
"""
Shared CLI utilities: error handling decorator, output helpers, confirmation.
"""

from functools import wraps
from pathlib import Path
from typing import Callable, Optional

import typer
from rich.console import Console

from ..core.errors import DevkitError

console = Console()
err_console = Console(stderr=True)


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
