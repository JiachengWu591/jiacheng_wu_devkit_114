# -*- coding: utf-8 -*-
"""
`devkit batch` command group: batch rename and organize, both backed by the same
move-plan engine in core.batch and the same three-layer safety mechanism:
  1. The full (old -> new) plan is always printed before anything happens.
  2. Collisions (duplicate targets, or a target that already exists outside the plan)
     are checked before touching any file; if found, the command refuses outright.
  3. Without --dry-run or --yes, an interactive confirmation is required.
--dry-run stops right after step 2, so a clean --dry-run really does mean the real run
would succeed—it's a full preview, not just a printout of the plan.
"""

from enum import Enum
from pathlib import Path
from typing import Annotated, Optional, Sequence

import typer

from ..core.batch import (
    MovePlanItem,
    apply_plan,
    build_organize_plan,
    build_rename_plan,
    expand_glob,
    find_collisions,
)
from ..core.errors import BatchError
from ._common import catch_devkit_errors, console

app = typer.Typer(help="Batch rename or organize files, with a preview + confirmation safety net.")


class OrganizeBy(str, Enum):
    ext = "ext"
    mtime = "mtime"


def _print_plan(plan: Sequence[MovePlanItem]) -> None:
    for item in plan:
        console.print(f"{item.src} -> {item.dst}")


def _confirm_or_abort(prompt: str, *, yes: bool) -> None:
    if yes:
        return
    if not typer.confirm(prompt):
        console.print("[yellow]Aborted, no files changed.[/yellow]")
        raise typer.Exit(code=0)


@app.command("rename")
@catch_devkit_errors
def rename_cmd(
    pattern: Annotated[
        str,
        typer.Argument(help="Glob pattern, e.g. '*.jpg' or 'reports/**/*.pdf' (** matches recursively)."),
    ],
    template: Annotated[
        str,
        typer.Option(
            "--template",
            help="New name template, e.g. '{stem}_{seq:03d}{ext}'. Fields: {seq} {stem} {ext} {name} {parent}.",
        ),
    ],
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print the rename plan (after checking for collisions) and exit; no files are touched."),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help=(
                "Skip the interactive confirmation. Required for non-interactive callers "
                "(scripts/CI/AI agents)—without it the command blocks waiting for stdin."
            ),
        ),
    ] = False,
) -> None:
    """
    Batch-rename files matching a glob pattern using a template.

    Files are numbered in sorted-path order starting at 1 ({seq}). The plan is always
    printed first. If any two files would land on the same target, or a target already
    exists outside this plan, the command refuses and makes no changes—this check runs even
    under --dry-run, so a clean --dry-run guarantees the real run will succeed too.

    Examples:

        devkit batch rename "*.jpg" --template "{stem}_{seq:03d}{ext}" --dry-run

        devkit batch rename "*.jpg" --template "{stem}_{seq:03d}{ext}" --yes
    """
    paths = expand_glob(pattern)
    if not paths:
        console.print(f"[yellow]No files matched pattern {pattern!r}.[/yellow]")
        return

    plan = build_rename_plan(paths, template)
    _print_plan(plan)

    collisions = find_collisions(plan)
    if collisions:
        raise BatchError(
            f"{len(collisions)} destination path(s) would conflict: "
            f"{[str(p) for p in collisions]}. Adjust --template or resolve manually."
        )

    if dry_run:
        return

    _confirm_or_abort(f"Rename {len(plan)} file(s)?", yes=yes)

    applied = apply_plan(plan, overwrite=False)
    console.print(f"[green]Renamed {len(applied)} file(s).[/green]")


@app.command("organize")
@catch_devkit_errors
def organize_cmd(
    src_dir: Annotated[
        Path,
        typer.Argument(exists=True, file_okay=False, help="Directory to organize."),
    ],
    by: Annotated[
        OrganizeBy,
        typer.Option("--by", help="Group files by file extension or by last-modified date."),
    ] = OrganizeBy.ext,
    dest: Annotated[
        Optional[Path],
        typer.Option("--dest", help="Root directory to move files into. Default: src_dir itself."),
    ] = None,
    date_format: Annotated[
        str,
        typer.Option("--date-format", help="strftime pattern for '--by mtime' subfolders, e.g. '%Y-%m'."),
    ] = "%Y-%m",
    recursive: Annotated[
        bool,
        typer.Option("--recursive", help="Also include files in subdirectories of src_dir."),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print the organize plan (after checking for collisions) and exit; no files are touched."),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help=(
                "Skip the interactive confirmation. Required for non-interactive callers "
                "(scripts/CI/AI agents)—without it the command blocks waiting for stdin."
            ),
        ),
    ] = False,
) -> None:
    """
    Organize files in a directory into subfolders grouped by extension or modified date.

    Without --recursive, only files directly inside src_dir are considered (files already
    sorted into subfolders from a previous run are left alone). The plan is always printed
    first; conflicting or pre-existing destinations abort the command with no changes made—
    this check runs even under --dry-run, so a clean --dry-run guarantees the real run will
    succeed too.

    Examples:

        devkit batch organize ./Downloads --by ext --dry-run

        devkit batch organize ./Downloads --by mtime --date-format "%Y-%m" --yes
    """
    dest_root = dest or src_dir
    pattern = "**/*" if recursive else "*"
    paths = expand_glob(pattern, root=src_dir)

    if not paths:
        console.print(f"[yellow]No files found in {src_dir}.[/yellow]")
        return

    plan = build_organize_plan(paths, by=by.value, dest_root=dest_root, date_format=date_format)
    _print_plan(plan)

    collisions = find_collisions(plan)
    if collisions:
        raise BatchError(
            f"{len(collisions)} destination path(s) would conflict: "
            f"{[str(p) for p in collisions]}. Resolve manually before retrying."
        )

    if dry_run:
        return

    _confirm_or_abort(f"Move {len(plan)} file(s)?", yes=yes)

    applied = apply_plan(plan, overwrite=False)
    console.print(f"[green]Moved {len(applied)} file(s).[/green]")
