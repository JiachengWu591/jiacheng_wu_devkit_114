# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from jiacheng_wu_devkit_114.core.convert import (
    detect_format,
    read_data,
    flatten_dict,
    dump_data,
    convert_data,
    parse_page_spec,
    pdf_to_markdown,
)
from jiacheng_wu_devkit_114.core.errors import ConversionError

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TWO_PAGE_PDF = FIXTURES_DIR / "two_page_sample.pdf"


# ------------------------------------------------------------------------------
# detect_format
# ------------------------------------------------------------------------------
def test_detect_format_json(tmp_path):
    assert detect_format(tmp_path / "a.json") == "json"


def test_detect_format_yaml_and_yml(tmp_path):
    assert detect_format(tmp_path / "a.yaml") == "yaml"
    assert detect_format(tmp_path / "a.yml") == "yaml"


def test_detect_format_csv(tmp_path):
    assert detect_format(tmp_path / "a.csv") == "csv"


def test_detect_format_unknown_suffix_raises(tmp_path):
    with pytest.raises(ConversionError):
        detect_format(tmp_path / "a.txt")


# ------------------------------------------------------------------------------
# read_data
# ------------------------------------------------------------------------------
def test_read_data_json(tmp_path):
    p = tmp_path / "a.json"
    p.write_text('{"x": 1, "y": "hi"}', encoding="utf-8")
    assert read_data(p, "json") == {"x": 1, "y": "hi"}


def test_read_data_json_with_utf8_bom(tmp_path):
    # Common on Windows: PowerShell's `Out-File -Encoding utf8` writes a leading BOM.
    p = tmp_path / "a.json"
    p.write_text('{"x": 1}', encoding="utf-8-sig")
    assert read_data(p, "json") == {"x": 1}


def test_read_data_yaml(tmp_path):
    p = tmp_path / "a.yaml"
    p.write_text("x: 1\ny: hi\n", encoding="utf-8")
    assert read_data(p, "yaml") == {"x": 1, "y": "hi"}


def test_read_data_csv(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text("name,age\nAlice,30\nBob,25\n", encoding="utf-8")
    result = read_data(p, "csv")
    assert result == [
        {"name": "Alice", "age": "30"},
        {"name": "Bob", "age": "25"},
    ]


def test_read_data_bad_json_raises(tmp_path):
    p = tmp_path / "a.json"
    p.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ConversionError):
        read_data(p, "json")


def test_read_data_unsupported_format_raises(tmp_path):
    p = tmp_path / "a.json"
    p.write_text("{}", encoding="utf-8")
    with pytest.raises(ConversionError):
        read_data(p, "xml")


# ------------------------------------------------------------------------------
# flatten_dict
# ------------------------------------------------------------------------------
def test_flatten_dict_nested():
    nested = {"address": {"city": "NY", "zip": "10001"}, "name": "Alice"}
    assert flatten_dict(nested) == {
        "address.city": "NY",
        "address.zip": "10001",
        "name": "Alice",
    }


def test_flatten_dict_with_list_value():
    nested = {"tags": ["a", "b"], "name": "Alice"}
    flattened = flatten_dict(nested)
    assert flattened["name"] == "Alice"
    assert flattened["tags"] == '["a", "b"]'


def test_flatten_dict_deeply_nested():
    nested = {"a": {"b": {"c": 1}}}
    assert flatten_dict(nested) == {"a.b.c": 1}


# ------------------------------------------------------------------------------
# dump_data
# ------------------------------------------------------------------------------
def test_dump_data_json():
    result = dump_data({"x": 1}, "json")
    assert '"x": 1' in result


def test_dump_data_yaml():
    result = dump_data({"x": 1}, "yaml")
    assert "x: 1" in result


def test_dump_data_csv_flat_records():
    records = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    result = dump_data(records, "csv")
    assert "name,age" in result
    assert "Alice,30" in result
    assert "Bob,25" in result


def test_dump_data_csv_single_dict_wrapped():
    result = dump_data({"name": "Alice"}, "csv")
    assert "name" in result
    assert "Alice" in result


def test_dump_data_csv_nested_without_flatten_raises():
    records = [{"name": "Alice", "address": {"city": "NY"}}]
    with pytest.raises(ConversionError, match="address"):
        dump_data(records, "csv", flatten=False)


def test_dump_data_csv_nested_with_flatten_succeeds():
    records = [{"name": "Alice", "address": {"city": "NY"}}]
    result = dump_data(records, "csv", flatten=True)
    assert "address.city" in result
    assert "NY" in result


def test_dump_data_csv_union_of_keys_across_records():
    records = [{"a": 1}, {"b": 2}]
    result = dump_data(records, "csv")
    header = result.splitlines()[0]
    assert "a" in header and "b" in header


def test_dump_data_csv_scalar_list_raises():
    with pytest.raises(ConversionError):
        dump_data([1, 2, 3], "csv")


def test_dump_data_csv_non_list_non_dict_raises():
    with pytest.raises(ConversionError):
        dump_data("just a string", "csv")


def test_dump_data_unsupported_format_raises():
    with pytest.raises(ConversionError):
        dump_data({"x": 1}, "xml")


# ------------------------------------------------------------------------------
# convert_data (end-to-end orchestration)
# ------------------------------------------------------------------------------
def test_convert_data_json_to_yaml(tmp_path):
    src = tmp_path / "a.json"
    src.write_text('{"x": 1}', encoding="utf-8")
    result = convert_data(src, "yaml")
    assert "x: 1" in result


def test_convert_data_csv_to_json(tmp_path):
    src = tmp_path / "a.csv"
    src.write_text("name,age\nAlice,30\n", encoding="utf-8")
    result = convert_data(src, "json")
    assert '"name": "Alice"' in result
    assert '"age": "30"' in result


def test_convert_data_explicit_from_format_overrides_suffix(tmp_path):
    # File has .txt suffix (undetectable) but content is valid json; explicit from_format bypasses detection.
    src = tmp_path / "a.txt"
    src.write_text('{"x": 1}', encoding="utf-8")
    result = convert_data(src, "yaml", from_format="json")
    assert "x: 1" in result


# ------------------------------------------------------------------------------
# parse_page_spec
# ------------------------------------------------------------------------------
def test_parse_page_spec_single_range():
    assert parse_page_spec("1-5") == [0, 1, 2, 3, 4]


def test_parse_page_spec_mixed_tokens():
    assert parse_page_spec("1,3,7-9") == [0, 2, 6, 7, 8]


def test_parse_page_spec_dedup_and_sort():
    assert parse_page_spec("3,1,2-2,1") == [0, 1, 2]


def test_parse_page_spec_zero_raises():
    with pytest.raises(ConversionError):
        parse_page_spec("0-3")


def test_parse_page_spec_reversed_range_raises():
    with pytest.raises(ConversionError):
        parse_page_spec("5-1")


def test_parse_page_spec_non_integer_raises():
    with pytest.raises(ConversionError):
        parse_page_spec("a-b")


def test_parse_page_spec_empty_raises():
    with pytest.raises(ConversionError):
        parse_page_spec("")


def test_parse_page_spec_too_many_dashes_raises():
    with pytest.raises(ConversionError):
        parse_page_spec("1-2-3")


def test_parse_page_spec_single_token_non_integer_raises():
    with pytest.raises(ConversionError):
        parse_page_spec("abc")


def test_parse_page_spec_single_token_zero_raises():
    with pytest.raises(ConversionError):
        parse_page_spec("0")


def test_pdf_to_markdown_wraps_underlying_failure(tmp_path):
    # A .pdf file with binary content that can't be parsed as a PDF (or gracefully
    # reinterpreted as plain text, which markitdown's format sniffing falls back to for
    # actually-text-like garbage). pdf_to_markdown must wrap the resulting failure into a
    # ConversionError rather than leaking it raw.
    bad_pdf = tmp_path / "corrupt.pdf"
    bad_pdf.write_bytes(bytes([0xFF, 0xD8, 0x00, 0x01, 0x02, 0x03, 0xC0, 0xC1]) * 20)
    with pytest.raises(ConversionError):
        pdf_to_markdown(bad_pdf)


# ------------------------------------------------------------------------------
# pdf_to_markdown
# ------------------------------------------------------------------------------
def test_pdf_to_markdown_full_document():
    md = pdf_to_markdown(TWO_PAGE_PDF)
    assert "Page one content" in md
    assert "Page two content" in md


def test_pdf_to_markdown_page_subset():
    md = pdf_to_markdown(TWO_PAGE_PDF, pages="1")
    assert "Page one content" in md
    assert "Page two content" not in md


def test_pdf_to_markdown_page_out_of_range_raises():
    with pytest.raises(ConversionError, match="out of range"):
        pdf_to_markdown(TWO_PAGE_PDF, pages="5")


def test_pdf_to_markdown_missing_markitdown_extra_raises_friendly_error(monkeypatch):
    # markitdown is an optional extra (pyproject.toml [pdf]), not a base dependency, so a
    # missing install must surface as a ConversionError with an install hint, not a raw
    # ModuleNotFoundError. Simulate "not installed" by making the import fail.
    monkeypatch.setitem(__import__("sys").modules, "markitdown", None)
    with pytest.raises(ConversionError, match=r"pip install jiacheng-wu-devkit-114\[pdf\]"):
        pdf_to_markdown(TWO_PAGE_PDF)


def test_pdf_to_markdown_missing_pypdf_extra_raises_friendly_error(monkeypatch):
    # Same as above, but for the pypdf import used only on the --pages subset path.
    monkeypatch.setitem(__import__("sys").modules, "pypdf", None)
    with pytest.raises(ConversionError, match=r"pip install jiacheng-wu-devkit-114\[pdf\]"):
        pdf_to_markdown(TWO_PAGE_PDF, pages="1")


def test_pdf_to_markdown_missing_file_raises(tmp_path):
    with pytest.raises(ConversionError):
        pdf_to_markdown(tmp_path / "missing.pdf")


def test_pdf_to_markdown_wrong_suffix_raises(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("hi", encoding="utf-8")
    with pytest.raises(ConversionError):
        pdf_to_markdown(p)


if __name__ == "__main__":
    from jiacheng_wu_devkit_114.tests import run_cov_test

    run_cov_test(
        __file__,
        "jiacheng_wu_devkit_114.core.convert",
        preview=False,
    )
