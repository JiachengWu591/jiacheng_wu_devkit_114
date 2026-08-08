# -*- coding: utf-8 -*-

from datetime import datetime

import pytest

from jiacheng_wu_devkit_114.core.log import (
    DEFAULT_LOG_PATTERN,
    compile_log_pattern,
    parse_log_lines,
    filter_entries,
    compute_level_counts,
    compute_top_messages,
    compute_stats,
)
from jiacheng_wu_devkit_114.core.errors import LogParseError

SAMPLE_LOG = """\
2026-08-07 10:23:45 INFO Starting job
2026-08-07 10:23:46 ERROR Connection refused
Traceback (most recent call last):
  File "app.py", line 10, in <module>
    raise ConnectionError("refused")
ConnectionError: refused
2026-08-07 10:23:47 INFO Job finished
2026-08-07 10:24:00 ERROR Connection refused
"""


def _lines(text: str) -> list[str]:
    return text.splitlines()


# ------------------------------------------------------------------------------
# compile_log_pattern
# ------------------------------------------------------------------------------
def test_compile_log_pattern_none_returns_default():
    assert compile_log_pattern(None) is DEFAULT_LOG_PATTERN


def test_compile_log_pattern_custom_valid():
    pattern = compile_log_pattern(r"^(?P<level>\w+)\|(?P<timestamp>\S+)\|(?P<message>.*)$")
    assert pattern.match("ERROR|123|boom")


def test_compile_log_pattern_invalid_regex_raises():
    with pytest.raises(LogParseError):
        compile_log_pattern("[unclosed")


def test_compile_log_pattern_missing_groups_raises():
    with pytest.raises(LogParseError, match="message"):
        compile_log_pattern(r"^(?P<timestamp>\S+) (?P<level>\w+)$")


# ------------------------------------------------------------------------------
# parse_log_lines
# ------------------------------------------------------------------------------
def test_parse_log_lines_basic_entries():
    entries = parse_log_lines(_lines("2026-08-07 10:23:45 INFO Starting job"))
    assert len(entries) == 1
    e = entries[0]
    assert e.level == "INFO"
    assert e.message == "Starting job"
    assert e.timestamp == datetime(2026, 8, 7, 10, 23, 45)
    assert e.line_no == 1


def test_parse_log_lines_multiline_traceback_absorbed():
    entries = parse_log_lines(_lines(SAMPLE_LOG))
    levels = [e.level for e in entries]
    assert levels == ["INFO", "ERROR", "INFO", "ERROR"]

    error_entry = entries[1]
    assert error_entry.message == "Connection refused"
    assert "Traceback (most recent call last):" in error_entry.raw
    assert "ConnectionError: refused" in error_entry.raw


def test_parse_log_lines_leading_unmatched_becomes_unknown_entry():
    text = "some preamble\nmore preamble\n2026-08-07 10:23:45 INFO Starting job"
    entries = parse_log_lines(_lines(text))
    assert entries[0].level == "UNKNOWN"
    assert entries[0].raw == "some preamble\nmore preamble"
    assert entries[1].level == "INFO"


def test_parse_log_lines_comma_millis_and_t_separator():
    entries = parse_log_lines(_lines("2026-08-07T10:23:45,123 DEBUG tick"))
    assert entries[0].timestamp == datetime(2026, 8, 7, 10, 23, 45, 123000)


def test_parse_log_lines_empty_input():
    assert parse_log_lines([]) == []


def test_parse_log_lines_custom_pattern():
    pattern = compile_log_pattern(r"^(?P<level>\w+)\|(?P<timestamp>\S+)\|(?P<message>.*)$")
    entries = parse_log_lines(_lines("ERROR|2026-08-07|boom"), pattern=pattern)
    assert entries[0].level == "ERROR"
    assert entries[0].message == "boom"
    # timestamp text doesn't match any known strptime format -> None, not an error.
    assert entries[0].timestamp is None


# ------------------------------------------------------------------------------
# filter_entries
# ------------------------------------------------------------------------------
def test_filter_entries_by_level():
    entries = parse_log_lines(_lines(SAMPLE_LOG))
    result = filter_entries(entries, levels=["ERROR"])
    assert all(e.level == "ERROR" for e in result)
    assert len(result) == 2


def test_filter_entries_by_keyword_matches_traceback_too():
    entries = parse_log_lines(_lines(SAMPLE_LOG))
    result = filter_entries(entries, keyword="ConnectionError")
    assert len(result) == 1
    assert result[0].level == "ERROR"


def test_filter_entries_by_time_range():
    entries = parse_log_lines(_lines(SAMPLE_LOG))
    result = filter_entries(entries, since=datetime(2026, 8, 7, 10, 23, 47))
    assert len(result) == 2
    assert all(e.timestamp >= datetime(2026, 8, 7, 10, 23, 47) for e in result)


def test_filter_entries_by_until():
    entries = parse_log_lines(_lines(SAMPLE_LOG))
    result = filter_entries(entries, until=datetime(2026, 8, 7, 10, 23, 46))
    assert len(result) == 2
    assert all(e.timestamp <= datetime(2026, 8, 7, 10, 23, 46) for e in result)


def test_filter_entries_excludes_unknown_timestamp_when_range_given():
    text = "garbage\n2026-08-07 10:23:45 INFO hi"
    entries = parse_log_lines(_lines(text))
    result = filter_entries(entries, since=datetime(2000, 1, 1))
    assert len(result) == 1
    assert result[0].level == "INFO"


def test_filter_entries_combined_filters_are_and():
    entries = parse_log_lines(_lines(SAMPLE_LOG))
    result = filter_entries(entries, levels=["ERROR"], keyword="finished")
    assert result == []


# ------------------------------------------------------------------------------
# compute_level_counts / compute_top_messages / compute_stats
# ------------------------------------------------------------------------------
def test_compute_level_counts():
    entries = parse_log_lines(_lines(SAMPLE_LOG))
    assert compute_level_counts(entries) == {"INFO": 2, "ERROR": 2}


def test_compute_top_messages_for_level():
    entries = parse_log_lines(_lines(SAMPLE_LOG))
    top = compute_top_messages(entries, level="ERROR", top_n=10)
    assert top == [("Connection refused", 2)]


def test_compute_top_messages_respects_top_n():
    text = "\n".join(f"2026-08-07 10:00:0{i} INFO msg{i}" for i in range(5))
    entries = parse_log_lines(_lines(text))
    top = compute_top_messages(entries, top_n=2)
    assert len(top) == 2


def test_compute_stats_level_grouping():
    entries = parse_log_lines(_lines(SAMPLE_LOG))
    stats = compute_stats(entries)
    assert stats["level_counts"] == {"INFO": 2, "ERROR": 2}
    assert stats["top_messages"]["ERROR"] == [("Connection refused", 2)]


def test_compute_stats_unsupported_group_by_raises():
    entries = parse_log_lines(_lines(SAMPLE_LOG))
    with pytest.raises(LogParseError):
        compute_stats(entries, group_by="message")


if __name__ == "__main__":
    from jiacheng_wu_devkit_114.tests import run_cov_test

    run_cov_test(
        __file__,
        "jiacheng_wu_devkit_114.core.log",
        preview=False,
    )
