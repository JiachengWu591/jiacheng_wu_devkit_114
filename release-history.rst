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

- ``markitdown``/``pypdf`` (needed only by ``devkit convert pdf2md``) are no longer installed
  by default — they're a heavy stack (onnxruntime, numpy, magika, ...) that most users of
  ``convert data``/``batch``/``log`` never need. Install them with the new ``pdf`` extra:
  ``pip install jiacheng-wu-devkit-114[pdf]``. Running ``pdf2md`` without it now raises a
  clear ``ConversionError`` pointing to that install command, instead of a raw
  ``ModuleNotFoundError`` traceback.

**Bugfixes**

- ``devkit batch rename``/``organize --dry-run`` now runs the collision check too, not just
  the plan preview. Previously ``--dry-run`` returned right after printing the plan, before
  ever calling the collision check, so a plan that would actually be rejected (two files
  landing on the same destination, or an existing file in the way) could preview as if it
  were clean under ``--dry-run`` and only fail once run for real. ``--dry-run`` now skips
  only the interactive confirmation, so a clean ``--dry-run`` is a genuine guarantee.
- ``commands/_common.py`` imports ``click`` directly (for ``devkit help``'s command-tree
  introspection), but ``click`` was never declared as a dependency in ``pyproject.toml``—it
  only happened to be present via some other package's transitive dependency in a full
  ``--all-extras`` dev install, which masked a base install (``pip install
  jiacheng-wu-devkit-114``) being completely broken (every command fails at import time with
  ``ModuleNotFoundError: No module named 'click'``). Added it as an explicit dependency.
- Error messages containing a literal ``[...]`` (e.g. the new "install it with ``pip install
  jiacheng-wu-devkit-114[pdf]``" hint) were silently missing that bracketed text entirely when
  printed: Rich's markup parser treats bare ``[word]`` as a style tag, and drops unrecognized
  ones rather than showing them as literal text. All error/status text is now escaped before
  being interpolated into a styled string.

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
