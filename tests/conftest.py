# -*- coding: utf-8 -*-
"""
Pytest configuration shared by the whole test suite.
"""

import pytest


@pytest.fixture(autouse=True)
def _stable_terminal_for_cli_help(monkeypatch):
    """
    Force a wide, colorless terminal for every test.

    Typer/Rich auto-detect terminal width and color support when rendering --help, and that
    detection is environment-dependent enough (observed: passes on a local Windows dev
    machine, fails on a Linux CI runner) to break plain assertions like
    "--dry-run" in result.stdout -- not because any real behavior changed, but because Rich
    injected ANSI color codes and/or word-wrapped a flag name across lines under a narrower
    detected width. Pinning COLUMNS wide and disabling color makes --help rendering
    deterministic across every environment this suite runs in.
    """
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("COLUMNS", "200")
    monkeypatch.setenv("LINES", "50")
