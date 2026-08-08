# -*- coding: utf-8 -*-
"""
Data format conversion: JSON/YAML/CSV interconversion, plus PDF to Markdown.
"""

import csv
import io
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from .errors import ConversionError

SUPPORTED_FORMATS = ("json", "yaml", "csv")

_SUFFIX_TO_FORMAT = {
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".csv": "csv",
}


def detect_format(path: Path) -> str:
    """
    Infer the data format ('json', 'yaml', or 'csv') from a file's suffix.

    Raises:
        ConversionError: if the suffix is not one of .json/.yaml/.yml/.csv.
    """
    fmt = _SUFFIX_TO_FORMAT.get(path.suffix.lower())
    if fmt is None:
        raise ConversionError(
            f"Cannot detect format from suffix {path.suffix!r} on {path}. "
            f"Supported suffixes: {sorted(_SUFFIX_TO_FORMAT)}."
        )
    return fmt


def read_data(path: Path, fmt: str) -> Any:
    """
    Read a file into a Python object according to fmt.

    - json/yaml -> whatever json.loads/yaml.safe_load returns (dict, list, or scalar)
    - csv       -> list[dict[str, str]] via csv.DictReader (values stay as strings; no type inference)

    Raises:
        ConversionError: if fmt is unsupported, or the file content cannot be parsed.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ConversionError(f"Unsupported format {fmt!r}. Supported: {SUPPORTED_FORMATS}.")

    # utf-8-sig transparently strips a leading BOM if present (common from Windows/PowerShell
    # editors) while behaving identically to utf-8 on files without one.
    text = path.read_text(encoding="utf-8-sig")
    try:
        if fmt == "json":
            return json.loads(text)
        elif fmt == "yaml":
            return yaml.safe_load(text)
        else:  # csv
            reader = csv.DictReader(io.StringIO(text))
            return list(reader)
    except (json.JSONDecodeError, yaml.YAMLError, csv.Error) as e:
        raise ConversionError(f"Failed to parse {path} as {fmt}: {e}") from e


def flatten_dict(d: Mapping[str, Any], parent_key: str = "", sep: str = ".") -> dict[str, Any]:
    """
    Recursively flatten a nested dict into a single-level dict with dotted keys.

    e.g. {"address": {"city": "NY"}} -> {"address.city": "NY"}

    Lists are not further flattened; they are JSON-encoded into a string value
    (documented limitation: list structure is preserved but not expanded into columns).
    """
    items: dict[str, Any] = {}
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, Mapping):
            items.update(flatten_dict(value, new_key, sep=sep))
        elif isinstance(value, list):
            items[new_key] = json.dumps(value, ensure_ascii=False)
        else:
            items[new_key] = value
    return items


def _find_nested_keys(record: Mapping[str, Any]) -> list[str]:
    """Return the keys in `record` whose value is itself a dict (would be lost/mangled by naive CSV)."""
    return [k for k, v in record.items() if isinstance(v, Mapping)]


def dump_data(data: Any, fmt: str, *, flatten: bool = False) -> str:
    """
    Serialize a Python object to text in the given format.

    For fmt='csv': `data` must be a list of dicts (or a single dict, treated as one record).
    If any record contains a nested dict and flatten=False, raises ConversionError naming the
    offending keys and suggesting --flatten or a non-CSV target. If flatten=True, each record is
    flattened first via flatten_dict(), and the header is the union of all keys across all
    records (missing cells left blank).

    Raises:
        ConversionError: on unsupported fmt, or CSV-incompatible data shape.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ConversionError(f"Unsupported format {fmt!r}. Supported: {SUPPORTED_FORMATS}.")

    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)

    if fmt == "yaml":
        return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)

    # fmt == "csv"
    if isinstance(data, Mapping):
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        raise ConversionError(
            f"Cannot convert {type(data).__name__} to csv: expected a list of records or a single object."
        )

    if not all(isinstance(r, Mapping) for r in records):
        raise ConversionError("Cannot convert to csv: every record must be an object (dict), not a scalar.")

    if not flatten:
        offending: dict[int, list[str]] = {}
        for i, record in enumerate(records):
            nested = _find_nested_keys(record)
            if nested:
                offending[i] = nested
        if offending:
            details = "; ".join(f"record {i}: {keys}" for i, keys in offending.items())
            raise ConversionError(
                f"Cannot convert to csv: nested objects found in {details}. "
                f"Use --flatten to dot-expand nested keys, or choose a non-csv target format."
            )
        prepared = records
    else:
        prepared = [flatten_dict(r) for r in records]

    fieldnames: list[str] = []
    seen: set[str] = set()
    for record in prepared:
        for key in record.keys():
            if key not in seen:
                seen.add(key)
                fieldnames.append(key)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, restval="")
    writer.writeheader()
    writer.writerows(prepared)
    return buf.getvalue()


def convert_data(
    input_path: Path,
    to_format: str,
    *,
    from_format: str | None = None,
    flatten: bool = False,
) -> str:
    """
    Convert the contents of `input_path` to `to_format`, returning the serialized text.

    If from_format is None, it is inferred from input_path's suffix via detect_format().

    Raises:
        ConversionError: propagated from detect_format/read_data/dump_data.
    """
    fmt = from_format or detect_format(input_path)
    data = read_data(input_path, fmt)
    return dump_data(data, to_format, flatten=flatten)


def parse_page_spec(spec: str) -> list[int]:
    """
    Parse a 1-indexed, comma/range page spec into a sorted, de-duplicated list of
    0-indexed page numbers (the format pypdf's page indexing expects).

    Examples: "1-5" -> [0, 1, 2, 3, 4]; "1,3,7-9" -> [0, 2, 6, 7, 8]

    Raises:
        ConversionError: on malformed tokens, non-positive numbers, or reversed ranges (e.g. "5-1").
    """
    pages: set[int] = set()
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            parts = token.split("-")
            if len(parts) != 2:
                raise ConversionError(f"Invalid page range token {token!r} in page spec {spec!r}.")
            start_str, end_str = parts
            try:
                start, end = int(start_str), int(end_str)
            except ValueError:
                raise ConversionError(f"Invalid page range token {token!r} in page spec {spec!r}: not integers.")
            if start < 1 or end < 1:
                raise ConversionError(f"Page numbers must be positive (1-indexed), got {token!r}.")
            if start > end:
                raise ConversionError(f"Invalid page range {token!r}: start ({start}) is after end ({end}).")
            pages.update(range(start - 1, end))
        else:
            try:
                page = int(token)
            except ValueError:
                raise ConversionError(f"Invalid page token {token!r} in page spec {spec!r}: not an integer.")
            if page < 1:
                raise ConversionError(f"Page numbers must be positive (1-indexed), got {token!r}.")
            pages.add(page - 1)

    if not pages:
        raise ConversionError(f"Page spec {spec!r} did not yield any pages.")

    return sorted(pages)


def _extract_pages(input_path: Path, page_indices: list[int]) -> io.BytesIO:
    """
    Extract the given 0-indexed pages from a PDF into an in-memory PDF buffer via pypdf.

    Raises:
        ConversionError: if any requested page index is out of range for the document.
    """
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(input_path))
    page_count = len(reader.pages)
    out_of_range = [i + 1 for i in page_indices if i >= page_count]
    if out_of_range:
        raise ConversionError(f"Page(s) {out_of_range} out of range: {input_path} has {page_count} page(s).")

    writer = PdfWriter()
    for i in page_indices:
        writer.add_page(reader.pages[i])

    buffer = io.BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer


def pdf_to_markdown(input_path: Path, *, pages: str | None = None) -> str:
    """
    Convert a PDF to Markdown text via markitdown.

    pages=None converts the whole document; otherwise parse_page_spec(pages) selects a
    1-indexed subset (e.g. "1-5" or "1,3,7-9") by first extracting just those pages into
    an in-memory PDF via pypdf, then converting that subset.

    Raises:
        ConversionError: if input_path doesn't exist, isn't a .pdf, a requested page is out
        of range, or the underlying conversion raises.
    """
    if not input_path.exists():
        raise ConversionError(f"PDF file not found: {input_path}")
    if input_path.suffix.lower() != ".pdf":
        raise ConversionError(f"Expected a .pdf file, got {input_path.suffix!r}: {input_path}")

    # Imported lazily: markitdown pulls in a fairly heavy stack (onnxruntime, pillow, etc.),
    # and `convert data` / `batch` / `log` commands shouldn't pay its import cost at CLI startup.
    from markitdown import MarkItDown, StreamInfo

    md = MarkItDown()
    try:
        if pages is None:
            result = md.convert(str(input_path))
        else:
            buffer = _extract_pages(input_path, parse_page_spec(pages))
            result = md.convert_stream(buffer, stream_info=StreamInfo(extension=".pdf", mimetype="application/pdf"))
    except ConversionError:
        raise
    except Exception as e:
        raise ConversionError(f"Failed to convert {input_path} to markdown: {e}") from e
    return result.text_content
