# -*- coding: utf-8 -*-
"""
`devkit convert` command group: data format conversion and PDF to Markdown.
"""

from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer

from ..core.convert import convert_data, pdf_to_markdown
from ._common import catch_devkit_errors, output_text

app = typer.Typer(help="Convert between JSON/YAML/CSV, and PDF to Markdown.")


class DataFormat(str, Enum):
    json = "json"
    yaml = "yaml"
    csv = "csv"


@app.command("data")
@catch_devkit_errors
def data_cmd(
    input_file: Annotated[
        Path,
        typer.Argument(exists=True, dir_okay=False, help="Source .json/.yaml/.yml/.csv file."),
    ],
    to: Annotated[
        DataFormat,
        typer.Option("--to", help="Target format: json, yaml, or csv."),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write result to this file instead of printing to stdout."),
    ] = None,
    flatten: Annotated[
        bool,
        typer.Option(
            "--flatten",
            help=(
                "Only relevant when --to csv and records contain nested objects (e.g. "
                '{"address": {"city": "NY"}}). Dot-expands nested keys (address.city) instead '
                "of failing. Ignored for json/yaml targets."
            ),
        ),
    ] = False,
) -> None:
    """
    Convert a JSON/YAML/CSV file to another of those three formats.

    Source format is inferred from the input file's suffix (.json, .yaml/.yml, .csv). CSV rows
    are read/written as flat string fields with no type inference. Converting to CSV requires
    each record to be a flat object; pass --flatten if any record has nested objects.

    Examples:

        devkit convert data users.json --to csv

        devkit convert data users.json --to csv --flatten

        devkit convert data config.yaml --to json -o config.json
    """
    result = convert_data(input_file, to.value, flatten=flatten)
    output_text(result, output)


@app.command("pdf2md")
@catch_devkit_errors
def pdf2md_cmd(
    input_file: Annotated[
        Path,
        typer.Argument(exists=True, dir_okay=False, help="Source .pdf file."),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Write Markdown to this file instead of printing to stdout."),
    ] = None,
    pages: Annotated[
        Optional[str],
        typer.Option(
            "--pages",
            help='1-indexed page selection, e.g. "1-5" or "1,3,7-9". Default: convert all pages.',
        ),
    ] = None,
) -> None:
    """
    Convert a PDF file to Markdown text.

    Uses pymupdf4llm for CPU-only, no-model-download conversion. Layout fidelity (multi-column
    pages, complex tables) is best-effort, not guaranteed.

    Examples:

        devkit convert pdf2md report.pdf -o report.md

        devkit convert pdf2md report.pdf --pages 1-3
    """
    result = pdf_to_markdown(input_file, pages=pages)
    output_text(result, output)
