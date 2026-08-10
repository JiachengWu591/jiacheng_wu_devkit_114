
.. image:: https://readthedocs.org/projects/jiacheng-wu-devkit-114/badge/?version=latest
    :target: https://jiacheng-wu-devkit-114.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/JiachengWu591/jiacheng_wu_devkit_114-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/JiachengWu591/jiacheng_wu_devkit_114-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/JiachengWu591/jiacheng_wu_devkit_114-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/JiachengWu591/jiacheng_wu_devkit_114-project

.. image:: https://img.shields.io/pypi/v/jiacheng-wu-devkit-114.svg
    :target: https://pypi.python.org/pypi/jiacheng-wu-devkit-114

.. image:: https://img.shields.io/pypi/l/jiacheng-wu-devkit-114.svg
    :target: https://pypi.python.org/pypi/jiacheng-wu-devkit-114

.. image:: https://img.shields.io/pypi/pyversions/jiacheng-wu-devkit-114.svg
    :target: https://pypi.python.org/pypi/jiacheng-wu-devkit-114

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/JiachengWu591/jiacheng_wu_devkit_114-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/JiachengWu591/jiacheng_wu_devkit_114-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://jiacheng-wu-devkit-114.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/JiachengWu591/jiacheng_wu_devkit_114-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/JiachengWu591/jiacheng_wu_devkit_114-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/JiachengWu591/jiacheng_wu_devkit_114-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/jiacheng-wu-devkit-114#files


Welcome to ``jiacheng_wu_devkit_114`` Documentation
==============================================================================
.. image:: https://jiacheng-wu-devkit-114.readthedocs.io/en/latest/_static/jiacheng_wu_devkit_114-logo.png
    :target: https://jiacheng-wu-devkit-114.readthedocs.io/en/latest/

``devkit`` is a small CLI toolkit for data conversion (JSON/YAML/CSV/PDF), batch file
renaming/organizing, and log filtering/summarizing. This page is a complete "from zero" user
guide: installation, a one-minute quick start, and the full command reference.

中文文档: `README.zh-CN.rst <https://github.com/JiachengWu591/jiacheng_wu_devkit_114-project/blob/main/README.zh-CN.rst>`_


.. _install:

What is devkit
--------------------------------------------------------------

``devkit`` is a small command-line toolkit that bundles three everyday file chores into a single tool, so you don't have to write a one-off script every time you need one of them. It has three independent command groups: ``convert`` (data format conversion between JSON/YAML/CSV, plus PDF-to-Markdown conversion), ``batch`` (batch-renaming and batch-organizing files), and ``log`` (filtering and summarizing plain-text log files). It's aimed at developers, sysadmins, and automation scripts (including AI agents) who want a dependable, scriptable utility for these common tasks without pulling in a bigger framework. This is a focused personal/example devkit, not a large framework — three practical utilities under one ``devkit`` command.

Installation
--------------------------------------------------------------

``devkit`` requires Python 3.10 or newer (it is tested on Python 3.10 through 3.14). Install it from PyPI with pip:

.. code-block:: console

    $ pip install jiacheng-wu-devkit-114

This installs the ``devkit`` command on your ``PATH``. To verify the install worked, run the help command:

.. code-block:: console

    $ devkit --help

You should see a short usage summary that lists three command groups: ``convert``, ``batch``, and ``log``. If you see those three listed, the install succeeded and you're ready to go.

Quick Start
--------------------------------------------------------------

Let's create a tiny example file and try two of ``devkit``'s commands back-to-back. This takes under a minute and touches nothing you didn't create yourself.

First, generate a small JSON file to play with:

.. code-block:: console

    $ python -c "import json; json.dump([{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}], open('people.json', 'w'))"

Now convert it to CSV and print the result to your terminal:

.. code-block:: console

    $ devkit convert data people.json --to csv

You should see something like:

.. code-block:: text

    name,age
    Alice,30
    Bob,25

Next, let's preview a rename plan for that file using ``devkit batch rename`` with ``--dry-run``, which is always safe because it never touches disk:

.. code-block:: console

    $ devkit batch rename "*.json" --template "{stem}_backup{ext}" --dry-run

``devkit`` always prints the *full, absolute* path of every file in the plan (shortened below to just the filename for readability); nothing is renamed yet:

.. code-block:: text

    .../people.json -> .../people_backup.json

That's the core idea: ``devkit`` shows you exactly what it's about to do, and (outside of ``--dry-run``) checks for conflicts and asks for confirmation before changing anything on disk. Read on for the full command reference.

Command Reference
--------------------------------------------------------------

``devkit`` organizes everything into three command groups, documented below: ``devkit convert``, ``devkit batch``, and ``devkit log``. There's also a fourth, standalone command, ``devkit help``, that searches across all of them at once.

devkit help
--------------------------------------------------------------

Run ``devkit help`` with no arguments to print a copy-paste-ready usage line for every
subcommand across all three groups, or ``devkit help KEYWORD`` to search for one. Each line
shows the command's actual signature (arguments, options, and defaults) rather than a
description — every command's file argument is shown as the generic placeholder ``input``, and
any ``--output``/``-o`` option as ``output``, so every row uses the same placeholder convention
instead of each command's own differently-named metavar (``input_file``, ``logfile``,
``src_dir``, ...). The keyword is matched case-insensitively against each command's name *and*
its full help text, so it finds commands even when the keyword never appears in the group name —
e.g. ``devkit help csv`` finds ``devkit convert data`` (csv is never in the word "convert"), and
``devkit help traceback`` finds ``devkit log filter``.

Example:

.. code-block:: console

    $ devkit help csv
    devkit convert data input --to <json|yaml|csv> [--output/-o output] [--flatten]

devkit convert
--------------------------------------------------------------

Convert between JSON/YAML/CSV, and convert PDF files to Markdown text. This group has two subcommands: ``data`` and ``pdf2md``.

**devkit convert data**

Run ``devkit convert data INPUT_FILE --to {json|yaml|csv}`` to convert a structured data file. The source format is auto-detected from ``INPUT_FILE``'s suffix (``.json``, ``.yaml``/``.yml``, or ``.csv``) — there is no option to override the detected source format.

Options:

- ``--to`` (required): the target format — one of ``json``, ``yaml``, or ``csv``.
- ``--output`` / ``-o``: write the result to a file instead of printing it to stdout. Optional.
- ``--flatten``: only relevant when ``--to csv`` and a record contains nested objects (e.g. ``{"address": {"city": "NY"}}``). Dot-expands nested keys into columns like ``address.city`` instead of failing. It is ignored (has no effect) when the target is ``json`` or ``yaml``.

Some things worth knowing:

- CSV rows are always read and written as flat string fields — there is no type inference, so numbers and booleans become strings.
- Converting to ``csv`` without ``--flatten`` fails with a clear error if any record has a nested object field; the error names the offending records/keys and suggests using ``--flatten`` or a non-csv target.
- When ``--flatten`` is used, list values inside a record are **not** expanded into separate columns — they are JSON-encoded into a single string cell. Only nested dicts get dot-expanded.
- When writing CSV, the header row is the union of all keys seen across all records; records missing a given key get a blank cell for it.
- JSON output uses 2-space indentation, and non-ASCII characters are kept literal (not escaped).
- YAML output allows unicode literally and preserves the source's key order (it is not alphabetically sorted).

Examples:

.. code-block:: console

    $ devkit convert data users.json --to csv
    $ devkit convert data users.json --to csv --flatten
    $ devkit convert data config.yaml --to json -o config.json

**devkit convert pdf2md**

Run ``devkit convert pdf2md INPUT_FILE`` to convert a PDF file to Markdown text, using the `markitdown <https://github.com/microsoft/markitdown>`_ library under the hood (MIT-licensed, CPU-only conversion). Layout fidelity for multi-column pages or complex tables is best-effort, not guaranteed.

Options:

- ``--output`` / ``-o``: write the resulting Markdown to a file instead of printing it to stdout. Optional.
- ``--pages``: an optional, 1-indexed page selection. Accepts a single range like ``"1-5"``, a comma list like ``"1,3,7"``, or a mix like ``"1,3,7-9"``. Omit it to convert the whole document.

An error is raised if the input file doesn't exist, doesn't end in ``.pdf``, or if ``--pages`` requests a page number beyond the document's actual page count.

Examples:

.. code-block:: console

    $ devkit convert pdf2md report.pdf -o report.md
    $ devkit convert pdf2md report.pdf --pages 1-3

devkit batch
--------------------------------------------------------------

Batch-rename or batch-organize (move into subfolders) files. Both subcommands share the same safety net described in full under `Safety Notes & Tips`_ below.

**devkit batch rename**

Run ``devkit batch rename PATTERN --template TEMPLATE`` to rename a set of files in place. ``PATTERN`` is a glob pattern (always quote it), and it supports ``**`` for recursive matching, e.g. ``"*.jpg"`` or ``"reports/**/*.pdf"``.

Options:

- ``--template`` (required): the new filename, written using Python ``str.format`` syntax. Available fields:

  - ``{seq}`` — the file's 1-based position among the matched files (matched files are sorted by path first, for deterministic, reproducible numbering). Supports format specs, e.g. ``{seq:03d}`` pads to 3 digits (``001``, ``002``, ...).
  - ``{stem}`` — the filename without its extension.
  - ``{ext}`` — the extension, including its leading dot (e.g. ``.jpg``), or an empty string if the file has no extension.
  - ``{name}`` — the original filename, including its extension.
  - ``{parent}`` — the name of the file's parent directory (just the directory's own name, not the full path).

  Using an unknown field name, or an invalid format spec, fails immediately with a clear error — before anything is renamed.
- ``--dry-run``: print the rename plan and exit; nothing is renamed and no confirmation is asked. Note: this only prints the plan — it does **not** run the collision check described below, so a plan that looks clean under ``--dry-run`` can still be refused when you actually run it.
- ``--yes`` / ``-y``: skip the interactive confirmation prompt and rename immediately (the collision check below still runs first either way).

Renaming happens in place — files stay in their current directory; only the filename changes.

Examples:

.. code-block:: console

    $ devkit batch rename "*.jpg" --template "{stem}_{seq:03d}{ext}" --dry-run
    $ devkit batch rename "*.jpg" --template "{stem}_{seq:03d}{ext}" --yes

**devkit batch organize**

Run ``devkit batch organize SRC_DIR`` to move files from ``SRC_DIR`` into subfolders. ``SRC_DIR`` must already exist and be a directory.

Options:

- ``--by``: bucketing strategy, either ``ext`` or ``mtime``. Default: ``ext``.

  - ``ext`` (the default): each file moves into a subfolder named after its lowercased extension without the dot (e.g. both ``.JPG`` and ``.jpg`` go into a folder named ``jpg``); files with no extension go into a folder named ``no_ext``.
  - ``mtime``: each file moves into a subfolder named by formatting the file's last-modified time using the ``--date-format`` pattern.
- ``--dest``: the root directory files get moved into. Defaults to ``SRC_DIR`` itself, so the result is ``SRC_DIR/<bucket>/<original filename>``.
- ``--date-format``: an strftime pattern, used only when ``--by mtime``. Default: ``"%Y-%m"`` (e.g. ``"2026-08"``).
- ``--recursive``: without it, only files directly inside ``SRC_DIR`` are considered, so files already sorted into subfolders by a previous run are left alone (safe to re-run). With ``--recursive``, files in subdirectories of ``SRC_DIR`` are included too.
- ``--dry-run``: print the move plan and exit; nothing is moved and no confirmation is asked (and, as with ``rename``, the collision check itself does not run in this mode).
- ``--yes`` / ``-y``: skip the interactive confirmation prompt and move immediately.

Examples:

.. code-block:: console

    $ devkit batch organize ./Downloads --by ext --dry-run
    $ devkit batch organize ./Downloads --by mtime --date-format "%Y-%m" --yes

devkit log
--------------------------------------------------------------

Filter and summarize plain-text log files. By default, ``devkit`` assumes lines look like a timestamp shaped like ``YYYY-MM-DD`` (with a space or ``T`` before the time) ``HH:MM:SS`` (optionally with ``.###`` or ``,###`` milliseconds), followed by whitespace, one of the levels ``DEBUG``/``INFO``/``WARNING``/``WARN``/``ERROR``/``CRITICAL`` **written in uppercase**, then whitespace, then the rest of the line as the message — for example: ``2026-08-07 10:01:12 ERROR Database connection timeout``.

.. note::
   The built-in pattern only recognizes the level word in uppercase. A line like ``2026-08-07 10:01:12 error Database connection timeout`` (lowercase ``error``) will **not** be recognized as an entry at all — it gets silently absorbed as a continuation line of whatever entry came before it (or into the leading ``UNKNOWN`` bucket if it's the first line in the file). If your logs use lowercase or mixed-case levels, pass a custom ``--pattern`` with a case-insensitive regex (e.g. prefix it with ``(?i)``).

Lines that don't match the pattern at all are appended as a continuation of the previous recognized entry, rather than being dropped or causing an error — this is what keeps multi-line stack traces/tracebacks correctly attached to the entry that produced them. Any unmatched lines appearing before the first recognized entry are collected into a single synthetic entry with level ``UNKNOWN``. Log files are read as UTF-8, transparently tolerating a leading BOM if present (e.g. from Windows editors).

Both subcommands below accept ``--pattern REGEX`` to use a custom line format instead of the default: a regular expression that **must** define three named capture groups — ``timestamp``, ``level``, and ``message``. If the regex is invalid, or is missing any of those three named groups, the command fails immediately with a clear error.

**devkit log filter**

Run ``devkit log filter LOGFILE`` to keep only the entries matching the filters you specify. All filters given at once combine with AND — an entry must satisfy every filter you passed.

Options:

- ``--level``: repeatable — pass it multiple times, e.g. ``--level ERROR --level CRITICAL``, to keep entries at any of the given levels (an OR across the levels you list). This comparison itself is case-insensitive; the caveat above is only about whether the default *parser* recognized the line as an entry in the first place. If omitted, all levels are kept.
- ``--keyword``: a case-insensitive substring match, checked against the entry's full text, including any multi-line traceback continuation lines, not only its first line.
- ``--since``: inclusive lower time bound, format ``YYYY-MM-DD`` or ``YYYY-MM-DD HH:MM:SS``.
- ``--until``: inclusive upper time bound, same format as ``--since``.
- ``--pattern``: custom line-format regex, as described above.
- ``--output`` / ``-o``: write the filtered entries to a file instead of printing to stdout.

Any entry whose timestamp couldn't be parsed (including ``UNKNOWN``-level leading entries) is automatically excluded whenever either ``--since`` or ``--until`` is given, since it can't be range-checked.

Examples:

.. code-block:: console

    $ devkit log filter app.log --level ERROR --level CRITICAL
    $ devkit log filter app.log --keyword timeout --since "2026-08-07 10:00:00"

**devkit log stats**

Run ``devkit log stats LOGFILE`` to summarize a log file's contents.

Options:

- ``--group-by``: currently only ``level`` is supported, and it is also the default — this groups the summary by log level.
- ``--top-n``: how many of the most frequent first-line messages to show per level. Default: ``10``.
- ``--pattern``: custom line-format regex, as described above.
- ``--json``: emit a single machine-readable JSON object instead of the human-readable text summary — recommended when scripting or piping into another tool or AI agent. Shape:

  .. code-block:: json

      {
        "level_counts": {"ERROR": 12, "INFO": 48},
        "top_messages": {"ERROR": [["Database connection timeout", 5]]}
      }

Without ``--json``, the output is a human-readable summary: one ``LEVEL: count`` line per level (sorted alphabetically by level name), followed by a ``Top messages for LEVEL:`` section per level listing its most frequent messages with counts.

Examples:

.. code-block:: console

    $ devkit log stats app.log
    $ devkit log stats app.log --top-n 5 --json

Safety Notes & Tips
--------------------------------------------------------------

**The batch safety net.** Both ``devkit batch rename`` and ``devkit batch organize`` work in three steps before they touch a single file:

1. **Print the plan.** The full list of planned moves (old path -> new path) is always printed first, using each file's full absolute path — this happens even with ``--dry-run``.
2. **Check for collisions.** Two files that would land on the same destination, or a destination that already exists on disk and isn't itself one of the plan's own source files, cause the command to refuse outright and make zero changes — not even a partial apply. Important: this check only runs when you are *not* using ``--dry-run``. ``--dry-run`` only prints the plan; it does not tell you whether the plan would actually be accepted. A plan that previews cleanly under ``--dry-run`` can still be rejected once you run it for real.
3. **Ask for confirmation.** Unless ``--dry-run`` or ``--yes``/``-y`` was given, the command interactively asks "Rename N file(s)?" / "Move N file(s)?" and requires a yes answer. This happens *after* the collision check in step 2, so a colliding plan is rejected before you'd even be asked to confirm it.

Since the collision check always runs on any non-``--dry-run`` invocation — including one with ``--yes`` — it's safe to run for real once you're satisfied with a ``--dry-run`` preview: if a collision exists, devkit will still catch it and refuse before touching any file.

**Always pass ``--yes`` in non-interactive contexts.** If you run ``devkit batch rename`` or ``devkit batch organize`` from a script, a CI pipeline, or an AI agent — anywhere with no human at a keyboard — the confirmation prompt from step 3 above will hang forever waiting on stdin that will never arrive. Always pass ``--yes`` (or ``-y``) in those contexts, or use ``--dry-run`` if you just want to inspect the plan.

**Quote your glob patterns.** Always wrap glob patterns in quotes — ``"*.jpg"``, not ``*.jpg`` — on every operating system, including Windows. ``devkit`` does its own recursive glob matching internally (supporting patterns like ``"reports/**/*.pdf"``), and it needs to receive the literal pattern text; if your shell expands the glob first, ``devkit`` never sees the pattern itself, only whatever files happened to match at that moment.

**Exit codes for scripting.** Two different situations produce a non-zero exit code:

- A file/directory argument that doesn't exist on disk (a typo'd path, for example) is rejected by the underlying CLI framework's own argument validation, before devkit's own logic ever runs. You'll see a boxed usage-error panel, and the process exits with code ``2``.
- Once the given paths do exist, a problem that's specific to devkit's own logic — a format mismatch, an ``--to csv`` target with unflattened nested objects, a batch plan with a collision, an invalid ``--pattern`` regex, an unsupported ``--group-by``, and so on — prints a red ``Error: ...`` message to stderr and exits with code ``1``.

Either way, a non-zero exit means nothing was changed. An unexpected internal bug (not a recognized input problem) would instead show a full Python traceback rather than either of the above.

For Contributors
--------------------------------------------------------------

If you're contributing to ``devkit`` itself (rather than just using it), the project uses a mise + uv based local dev workflow: ``mise run inst`` installs dependencies, ``mise run test`` runs the pytest suite, ``mise run cov`` runs tests with an HTML coverage report, and ``mise run build-doc`` builds the Sphinx documentation.
