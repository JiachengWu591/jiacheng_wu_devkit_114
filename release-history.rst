.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
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

**Bugfixes**

**Miscellaneous**


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
