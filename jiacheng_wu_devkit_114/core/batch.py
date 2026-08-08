# -*- coding: utf-8 -*-
"""
Batch file operations: rename and organize, sharing a common move-plan engine.

The engine always separates "compute the plan" (pure functions, no filesystem writes)
from "apply the plan" (the only function that touches disk), so callers can preview,
validate, and confirm before anything irreversible happens.
"""

import glob as glob_module
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence

from .errors import BatchError


@dataclass(frozen=True)
class MovePlanItem:
    src: Path
    dst: Path


def expand_glob(pattern: str, *, root: Optional[Path] = None) -> list[Path]:
    """
    Resolve a glob pattern (supports ** for recursive matching) into a sorted,
    de-duplicated list of existing files (directories are excluded).

    If `root` is given and `pattern` is not itself absolute, the pattern is resolved
    relative to `root`; otherwise relative to the current working directory. Sorting
    makes the {seq} numbering in render_name() deterministic across OS/filesystem order.
    """
    if Path(pattern).is_absolute():
        full_pattern = pattern
    else:
        full_pattern = str((root or Path.cwd()) / pattern)

    matches = glob_module.glob(full_pattern, recursive=True)
    return sorted({Path(m) for m in matches if Path(m).is_file()})


def render_name(template: str, *, seq: int, path: Path) -> str:
    """
    Render a new filename with str.format syntax. Available fields:
      {seq}    1-based position, supports format specs: {seq:03d}
      {stem}   filename without extension
      {ext}    extension WITH leading dot (e.g. '.jpg'), '' if none
      {name}   original full filename
      {parent} parent directory's own name (not full path)

    Raises:
        BatchError: on unknown field names or malformed format syntax.
    """
    fields = {
        "seq": seq,
        "stem": path.stem,
        "ext": path.suffix,
        "name": path.name,
        "parent": path.parent.name,
    }
    try:
        return template.format(**fields)
    except (KeyError, IndexError) as e:
        raise BatchError(f"Unknown field {e} in template {template!r}. Valid fields: {sorted(fields)}.") from e
    except ValueError as e:
        raise BatchError(f"Invalid format spec in template {template!r}: {e}") from e


def build_rename_plan(paths: Sequence[Path], template: str) -> list[MovePlanItem]:
    """
    Compute (src, dst) pairs for renaming each path in place (same directory), numbering
    them 1-based in the order given. Pure function: no filesystem I/O.
    """
    plan = []
    for i, path in enumerate(paths, start=1):
        new_name = render_name(template, seq=i, path=path)
        plan.append(MovePlanItem(src=path, dst=path.with_name(new_name)))
    return plan


def build_organize_plan(
    paths: Sequence[Path],
    *,
    by: str = "ext",
    dest_root: Path,
    date_format: str = "%Y-%m",
) -> list[MovePlanItem]:
    """
    Compute (src, dst) pairs for moving each path into a subfolder of dest_root:
      by='ext'   -> dest_root/<ext without dot, lowercased, or 'no_ext'>/<original filename>
      by='mtime' -> dest_root/<strftime(date_format, file mtime)>/<original filename>

    Reads each file's mtime when by='mtime' but performs no writes.

    Raises:
        BatchError: if `by` is not 'ext' or 'mtime'.
    """
    if by not in ("ext", "mtime"):
        raise BatchError(f"Unsupported --by value {by!r}. Supported: 'ext', 'mtime'.")

    plan = []
    for path in paths:
        if by == "ext":
            bucket = path.suffix.lstrip(".").lower() or "no_ext"
        else:
            bucket = datetime.fromtimestamp(path.stat().st_mtime).strftime(date_format)
        plan.append(MovePlanItem(src=path, dst=dest_root / bucket / path.name))
    return plan


def find_collisions(plan: Sequence[MovePlanItem]) -> list[Path]:
    """
    Return destination paths that are unsafe to write to without confirmation:
      - the destination of 2+ items in this plan, or
      - already existing on disk and not itself a source in this same plan
        (i.e. applying the plan would silently overwrite an unrelated existing file).
    """
    dest_counts: dict[Path, int] = {}
    for item in plan:
        dest_counts[item.dst] = dest_counts.get(item.dst, 0) + 1

    sources = {item.src for item in plan}
    collisions: set[Path] = set()
    for dst, count in dest_counts.items():
        if count > 1 or (dst.exists() and dst not in sources):
            collisions.add(dst)

    return sorted(collisions)


def apply_plan(plan: Sequence[MovePlanItem], *, overwrite: bool = False) -> list[MovePlanItem]:
    """
    Execute the moves in `plan`, creating missing parent directories as needed.

    Raises BatchError *before* touching any file if find_collisions(plan) is non-empty and
    overwrite=False—no partial application on a rejected plan. Moves are applied in plan
    order; a cyclic swap (e.g. a template that maps a->b and b->a within the same plan) is
    not specially handled and can clobber one of the files, so avoid templates that do that.

    Returns the items actually applied, in plan order.
    """
    if not overwrite:
        collisions = find_collisions(plan)
        if collisions:
            raise BatchError(
                f"Refusing to apply: {len(collisions)} destination path(s) would conflict: "
                f"{[str(p) for p in collisions]}. Adjust the template/options, or resolve manually."
            )

    applied = []
    for item in plan:
        item.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(item.src), str(item.dst))
        applied.append(item)
    return applied
