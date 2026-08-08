# -*- coding: utf-8 -*-
"""
Log analysis: parsing, filtering, and statistics.

Default format assumption: "YYYY-MM-DD[ T]HH:MM:SS[.,ms] LEVEL message" (the common shape
of Python logging output). Lines that don't match are treated as a continuation of the
previous entry (e.g. multi-line tracebacks), not dropped or errored on. Pass --pattern with
a custom regex (named groups: timestamp, level, message) for non-default formats.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Optional, Sequence

from .errors import LogParseError

DEFAULT_LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?)\s+"
    r"(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)\s+(?P<message>.*)$"
)

_REQUIRED_GROUPS = {"timestamp", "level", "message"}

_TIMESTAMP_FORMATS = (
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S,%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S,%f",
    "%Y-%m-%dT%H:%M:%S",
)


@dataclass(frozen=True)
class LogEntry:
    timestamp: Optional[datetime]  # None if unparsable, or for the leading UNKNOWN bucket
    level: str
    message: str  # the message captured on the entry's first line
    raw: str  # full original text, including any continuation lines, joined by "\n"
    line_no: int  # 1-indexed line number where this entry starts


def compile_log_pattern(pattern: Optional[str]) -> re.Pattern[str]:
    """
    Compile a custom log-line regex, or return DEFAULT_LOG_PATTERN if pattern is None.

    Raises:
        LogParseError: if the pattern is invalid regex, or missing required named groups
        'timestamp', 'level', 'message'.
    """
    if pattern is None:
        return DEFAULT_LOG_PATTERN
    try:
        compiled = re.compile(pattern)
    except re.error as e:
        raise LogParseError(f"Invalid regex {pattern!r}: {e}") from e

    missing = _REQUIRED_GROUPS - set(compiled.groupindex)
    if missing:
        raise LogParseError(f"Pattern {pattern!r} is missing required named group(s): {sorted(missing)}.")
    return compiled


def _parse_timestamp(text: str) -> Optional[datetime]:
    for fmt in _TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def parse_log_lines(lines: Iterable[str], *, pattern: re.Pattern[str] = DEFAULT_LOG_PATTERN) -> list[LogEntry]:
    """
    Turn raw lines into LogEntry records.

    A line not matching `pattern` is appended (as a continuation) to the entry currently
    being built—this is what correctly absorbs multi-line tracebacks. Leading lines that
    appear before any recognized entry are collected into a single level='UNKNOWN' entry.
    """
    entries: list[LogEntry] = []
    pending: Optional[dict[str, Any]] = None

    def flush() -> None:
        nonlocal pending
        if pending is not None:
            entries.append(
                LogEntry(
                    timestamp=pending["timestamp"],
                    level=pending["level"],
                    message=pending["message"],
                    raw="\n".join(pending["raw_lines"]),
                    line_no=pending["line_no"],
                )
            )
            pending = None

    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")
        match = pattern.match(line)
        if match:
            flush()
            pending = {
                "timestamp": _parse_timestamp(match.group("timestamp")),
                "level": match.group("level").upper(),
                "message": match.group("message"),
                "raw_lines": [line],
                "line_no": line_no,
            }
        elif pending is not None:
            pending["raw_lines"].append(line)
        else:
            pending = {
                "timestamp": None,
                "level": "UNKNOWN",
                "message": line,
                "raw_lines": [line],
                "line_no": line_no,
            }
    flush()
    return entries


def filter_entries(
    entries: Sequence[LogEntry],
    *,
    levels: Optional[Sequence[str]] = None,
    keyword: Optional[str] = None,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
) -> list[LogEntry]:
    """
    Filter entries with AND semantics across all provided filters.

    - `levels` matches if entry.level is in the set (case-insensitive); pass multiple values
      to get OR-across-levels behavior.
    - `keyword` is a case-insensitive substring match against the entry's full raw text
      (so it also matches inside multi-line tracebacks, not just the first line).
    - Entries with timestamp=None are excluded whenever since/until is given, since an
      unknown time can't be range-checked.
    """
    levels_upper = {lvl.upper() for lvl in levels} if levels else None
    keyword_lower = keyword.lower() if keyword else None
    needs_timestamp = since is not None or until is not None

    result = []
    for entry in entries:
        if levels_upper is not None and entry.level not in levels_upper:
            continue
        if keyword_lower is not None and keyword_lower not in entry.raw.lower():
            continue
        if needs_timestamp:
            if entry.timestamp is None:
                continue
            if since is not None and entry.timestamp < since:
                continue
            if until is not None and entry.timestamp > until:
                continue
        result.append(entry)
    return result


def compute_level_counts(entries: Sequence[LogEntry]) -> dict[str, int]:
    """Count entries per level."""
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry.level] = counts.get(entry.level, 0) + 1
    return counts


def compute_top_messages(
    entries: Sequence[LogEntry],
    *,
    level: Optional[str] = None,
    top_n: int = 10,
) -> list[tuple[str, int]]:
    """Most frequent first-line messages, optionally restricted to one level, most-common first."""
    counts: dict[str, int] = {}
    for entry in entries:
        if level is not None and entry.level != level.upper():
            continue
        counts[entry.message] = counts.get(entry.message, 0) + 1
    return sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:top_n]


def compute_stats(entries: Sequence[LogEntry], *, group_by: str = "level", top_n: int = 10) -> dict[str, Any]:
    """
    Orchestrate a stats view over `entries`.

    group_by='level' (the only supported value) returns:
        {'level_counts': {...}, 'top_messages': {level: [(msg, count), ...], ...}}

    Raises:
        LogParseError: if group_by is not 'level'.
    """
    if group_by != "level":
        raise LogParseError(f"Unsupported --group-by value {group_by!r}. Supported: 'level'.")

    level_counts = compute_level_counts(entries)
    top_messages = {level: compute_top_messages(entries, level=level, top_n=top_n) for level in sorted(level_counts)}
    return {"level_counts": level_counts, "top_messages": top_messages}
