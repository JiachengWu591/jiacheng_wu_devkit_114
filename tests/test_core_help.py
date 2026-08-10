# -*- coding: utf-8 -*-

from jiacheng_wu_devkit_114.core.help import CommandEntry, search_entries

ENTRIES = [
    CommandEntry(path="devkit convert data", usage="devkit convert data input --to <json|yaml|csv>", detail="Handles nested objects via --flatten."),
    CommandEntry(path="devkit batch rename", usage="devkit batch rename input --template <str>", detail="Uses a template with {seq} and {stem}."),
    CommandEntry(path="devkit log filter", usage="devkit log filter input [--level <str>]...", detail="Keeps multi-line tracebacks attached."),
]


def test_search_entries_no_keyword_returns_all_in_order():
    assert search_entries(ENTRIES, None) == ENTRIES


def test_search_entries_empty_string_returns_all():
    assert search_entries(ENTRIES, "") == ENTRIES


def test_search_entries_matches_path():
    result = search_entries(ENTRIES, "rename")
    assert result == [ENTRIES[1]]


def test_search_entries_matches_usage():
    result = search_entries(ENTRIES, "--level")
    assert result == [ENTRIES[2]]


def test_search_entries_matches_detail_only():
    result = search_entries(ENTRIES, "traceback")
    assert result == [ENTRIES[2]]


def test_search_entries_is_case_insensitive():
    assert search_entries(ENTRIES, "RENAME") == [ENTRIES[1]]


def test_search_entries_no_match_returns_empty_list():
    assert search_entries(ENTRIES, "nonexistent") == []


if __name__ == "__main__":
    from jiacheng_wu_devkit_114.tests import run_cov_test

    run_cov_test(
        __file__,
        "jiacheng_wu_devkit_114.core.help",
        preview=False,
    )
