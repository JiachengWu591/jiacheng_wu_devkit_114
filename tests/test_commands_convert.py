# -*- coding: utf-8 -*-

from pathlib import Path

from typer.testing import CliRunner

from jiacheng_wu_devkit_114.commands.convert import app

runner = CliRunner()

TWO_PAGE_PDF = Path(__file__).parent / "fixtures" / "two_page_sample.pdf"


def test_help_lists_flatten_option():
    result = runner.invoke(app, ["data", "--help"])
    assert result.exit_code == 0
    assert "flatten" in result.stdout


def test_data_json_to_yaml(tmp_path):
    src = tmp_path / "a.json"
    src.write_text('{"x": 1}', encoding="utf-8")
    result = runner.invoke(app, ["data", str(src), "--to", "yaml"])
    assert result.exit_code == 0
    assert "x: 1" in result.stdout


def test_data_writes_to_output_file(tmp_path):
    src = tmp_path / "a.json"
    src.write_text('{"x": 1}', encoding="utf-8")
    dst = tmp_path / "a.yaml"
    result = runner.invoke(app, ["data", str(src), "--to", "yaml", "-o", str(dst)])
    assert result.exit_code == 0
    assert dst.exists()
    assert "x: 1" in dst.read_text(encoding="utf-8")


def test_data_csv_nested_without_flatten_fails_cleanly(tmp_path):
    src = tmp_path / "a.json"
    src.write_text('{"name": "Alice", "address": {"city": "NY"}}', encoding="utf-8")
    result = runner.invoke(app, ["data", str(src), "--to", "csv"])
    assert result.exit_code == 1
    assert "address" in result.output


def test_data_csv_nested_with_flatten_succeeds(tmp_path):
    src = tmp_path / "a.json"
    src.write_text('{"name": "Alice", "address": {"city": "NY"}}', encoding="utf-8")
    result = runner.invoke(app, ["data", str(src), "--to", "csv", "--flatten"])
    assert result.exit_code == 0
    assert "address.city" in result.stdout


def test_data_invalid_to_value_rejected():
    result = runner.invoke(app, ["data", "whatever.json", "--to", "xml"])
    assert result.exit_code != 0


def test_data_missing_input_file_rejected():
    result = runner.invoke(app, ["data", "does_not_exist.json", "--to", "yaml"])
    assert result.exit_code != 0


def test_pdf2md_help_mentions_pages_option():
    result = runner.invoke(app, ["pdf2md", "--help"])
    assert result.exit_code == 0
    assert "--pages" in result.stdout


def test_pdf2md_full_document():
    result = runner.invoke(app, ["pdf2md", str(TWO_PAGE_PDF)])
    assert result.exit_code == 0
    assert "Page one content" in result.stdout
    assert "Page two content" in result.stdout


def test_pdf2md_page_subset():
    result = runner.invoke(app, ["pdf2md", str(TWO_PAGE_PDF), "--pages", "1"])
    assert result.exit_code == 0
    assert "Page one content" in result.stdout
    assert "Page two content" not in result.stdout


if __name__ == "__main__":
    from jiacheng_wu_devkit_114.tests import run_cov_test

    run_cov_test(
        __file__,
        "jiacheng_wu_devkit_114.commands.convert",
        preview=False,
    )
