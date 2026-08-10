# -*- coding: utf-8 -*-
"""
Command lookup: search across every devkit subcommand by keyword.
"""

from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True)
class CommandEntry:
    """
    One devkit subcommand, e.g. path="devkit batch rename".

    ``usage`` is the copy-paste-style signature shown to the user (e.g. "devkit batch rename
    input --template <str> [--dry-run]"). ``detail`` is the full help text (docstring), used
    only for search matching, never displayed.
    """

    path: str
    usage: str
    detail: str = ""


def search_entries(entries: Sequence[CommandEntry], keyword: Optional[str]) -> list[CommandEntry]:
    """
    Filter entries by a case-insensitive substring match against each entry's path,
    usage, and detail combined. keyword=None (or empty) returns every entry, unchanged order.
    """
    if not keyword:
        return list(entries)
    kw = keyword.lower()
    return [e for e in entries if kw in e.path.lower() or kw in e.usage.lower() or kw in e.detail.lower()]
