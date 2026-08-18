.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.2.0 (2026-08-17)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- New ``devkit help [KEYWORD]`` command: prints a copy-paste-ready usage signature for every
  subcommand across all three groups, or searches for one by keyword. Each command's file
  argument is shown as the generic placeholder ``input`` and any ``--output``/``-o`` option as
  ``output``, so every row uses the same placeholder convention instead of each command's own
  metavar. With no keyword it lists everything; with a keyword it matches case-insensitively
  against each command's name and full help text, so it finds a command even when the keyword
  never appears in its group name (e.g. ``devkit help csv`` finds ``devkit convert data``).

**Minor Improvements**

- ``markitdown``/``pypdf`` (needed only by ``devkit convert pdf2md``) are no longer installed
  by default — they're a heavy stack (onnxruntime, numpy, magika, ...) that most users of
  ``convert data``/``batch``/``log`` never need. Install them with the new ``pdf`` extra:
  ``pip install jiacheng-wu-devkit-114[pdf]``. Running ``pdf2md`` without it now raises a
  clear ``ConversionError`` pointing to that install command, instead of a raw
  ``ModuleNotFoundError`` traceback.
- CI now runs automatically on every push/PR (it had been manual-trigger-only), across the
  full ``ubuntu-latest``/``windows-latest`` × Python 3.10-3.13 matrix (Python 3.14 excluded
  for now: ``onnxruntime`` has no ``cp314`` wheel yet).

**Bugfixes**

- ``devkit batch rename``/``organize --dry-run`` now runs the collision check too, not just
  the plan preview. Previously ``--dry-run`` returned right after printing the plan, before
  ever calling the collision check, so a plan that would actually be rejected (two files
  landing on the same destination, or an existing file in the way) could preview as if it
  were clean under ``--dry-run`` and only fail once run for real. ``--dry-run`` now skips
  only the interactive confirmation, so a clean ``--dry-run`` is a genuine guarantee.
- A base install (``pip install jiacheng-wu-devkit-114``, no extras) was completely broken —
  every command failed at import time with ``ModuleNotFoundError: No module named 'click'``,
  since ``commands/_common.py`` imports ``click`` directly but it was never declared as a
  dependency. It only worked in local development because some other package in a full
  ``--all-extras`` install happened to pull it in transitively. Added it as an explicit
  dependency.
- Error messages containing a literal ``[...]`` (e.g. the ``pdf`` extra's install hint, ``pip
  install jiacheng-wu-devkit-114[pdf]``) were silently missing that bracketed text when
  printed: Rich's markup parser treats a bare ``[word]`` as a style tag and drops
  unrecognized ones instead of showing them literally. All error/status text is now escaped
  before being styled.
- ``devkit log stats --json`` could get ANSI color codes spliced into its output in
  environments that force color support (observed on GitHub Actions' Ubuntu runner),
  corrupting what's documented as machine-readable output for scripts/AI agents and breaking
  ``json.loads()`` on it. Switched to a plain, never-styled ``print()`` for that one output
  path, and disabled Rich's automatic content auto-highlighting on both console instances so
  no other plain data output (a YAML/CSV value, a path) can suffer the same corruption.
- Every GitHub URL in ``pyproject.toml`` (``Homepage``, ``Repository``, ``Issues``,
  ``Changelog``), both READMEs, and the maintainer guide pointed at
  ``jiacheng_wu_devkit_114-project`` — a repo name that 404s, since the actual repo is
  ``jiacheng_wu_devkit_114`` (no ``-project`` suffix), left over from the cookiecutter
  template assuming the local folder name matches the GitHub repo name. All fixed; this is
  also the first release where PyPI's own project links point at the right place. Also
  pointed the Codecov badge at ``app.codecov.io/github/...`` directly instead of the legacy
  ``codecov.io/gh/...`` redirect, which landed on an ambiguous "not found"/organization-picker
  page for a personal-account repo.
- Fixed a ``codecov-action@v5`` input name (``file`` renamed to ``files`` upstream) and a
  fragile CI caching step that skipped reinstalling dependencies on a cache hit even when the
  cached virtualenv referenced a Python interpreter that no longer existed on the runner,
  silently leaving ``pytest`` itself uninstalled.

**Miscellaneous**

- Documented the ``devkit help`` command and the ``pdf`` extra in both READMEs; rewrote the
  batch safety-net docs to describe the corrected ``--dry-run`` behavior.


0.1.0 (2026-08-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First release. Adds the ``devkit`` CLI toolkit with three command groups:

  - ``devkit convert``: interconvert JSON/YAML/CSV data files, and convert PDF files to
    Markdown text.
  - ``devkit batch``: batch-rename or batch-organize (by extension or modified date) files,
    backed by a shared move-plan engine with a three-layer safety mechanism (always preview
    the plan first, check for destination collisions, then require confirmation before
    touching any file).
  - ``devkit log``: filter and summarize plain-text log files by level, keyword, and time
    range, correctly keeping multi-line tracebacks attached to the log entry that produced
    them.

**Bugfixes**

- ``devkit convert pdf2md`` no longer depends on PyMuPDF/pymupdf4llm (AGPL-3.0, with a
  conflicting license for an MIT-licensed CLI). PDF-to-Markdown conversion now goes through
  ``markitdown`` and ``pypdf`` instead (both MIT/BSD), with identical ``--pages`` behavior.
- Fixed several ``mise.toml`` tasks (``venv-remove``, ``build-doc``, ``view-cov``,
  ``view-doc``, ``notebook-to-markdown``, and the publish/release/setup-* tasks) that only
  worked on Unix — they referenced Unix-only paths and shell commands, and relied on
  multi-line ``run`` scripts whose later lines mise silently never executed on Windows.
