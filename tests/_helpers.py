# -*- coding: utf-8 -*-
"""
Shared test-only helpers (not part of the published package).
"""

import re

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    """
    Remove ANSI SGR escape sequences (color/style codes) from `text`.

    Typer/Rich's --help rendering applies syntax highlighting to option names by splitting
    them into several separately-styled spans, e.g. "--dry-run" becomes
    "\\x1b[36m-\\x1b[0m\\x1b[36m-dry\\x1b[0m\\x1b[36m-run\\x1b[0m" whenever color output is
    active. Whether that happens is environment-dependent (observed: off on a local Windows
    dev machine, on under a Linux CI runner) and NO_COLOR doesn't reliably suppress it once
    something else has forced color on. Stripping the escape codes first makes substring
    assertions like "--dry-run" in stdout deterministic regardless of environment, since the
    literal text on either side of each code is otherwise unchanged and simply reassembles.
    """
    return _ANSI_RE.sub("", text)
