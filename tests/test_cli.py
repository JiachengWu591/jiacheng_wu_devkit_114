# -*- coding: utf-8 -*-

from typer.testing import CliRunner

from jiacheng_wu_devkit_114.cli import app

from _helpers import strip_ansi

runner = CliRunner()


def test_top_level_help_lists_three_groups():
    result = runner.invoke(app, ["--help"])
    stdout = strip_ansi(result.stdout)
    assert result.exit_code == 0
    for name in ("convert", "batch", "log"):
        assert name in stdout


def test_convert_group_reachable_from_top_level():
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    assert "pdf2md" in strip_ansi(result.stdout)


def test_batch_group_reachable_from_top_level():
    result = runner.invoke(app, ["batch", "--help"])
    stdout = strip_ansi(result.stdout)
    assert result.exit_code == 0
    assert "rename" in stdout
    assert "organize" in stdout


def test_log_group_reachable_from_top_level():
    result = runner.invoke(app, ["log", "--help"])
    stdout = strip_ansi(result.stdout)
    assert result.exit_code == 0
    assert "filter" in stdout
    assert "stats" in stdout


def test_top_level_help_mentions_help_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "devkit help" in strip_ansi(result.stdout)


def test_help_with_no_keyword_lists_every_command():
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 0
    for path in (
        "devkit convert data",
        "devkit convert pdf2md",
        "devkit batch rename",
        "devkit batch organize",
        "devkit log filter",
        "devkit log stats",
    ):
        assert path in result.stdout
    # The "help" command itself is not a searchable result.
    assert "devkit help" not in result.stdout


def test_help_keyword_matches_command_name_across_groups():
    # "csv" never appears in a group name, only in convert data's help text.
    result = runner.invoke(app, ["help", "csv"])
    assert result.exit_code == 0
    assert "devkit convert data" in result.stdout
    assert "devkit batch rename" not in result.stdout


def test_help_keyword_matches_full_help_text():
    # "traceback" only appears in log filter's docstring, not its short summary.
    result = runner.invoke(app, ["help", "traceback"])
    assert result.exit_code == 0
    assert "devkit log filter" in result.stdout


def test_help_keyword_is_case_insensitive():
    result = runner.invoke(app, ["help", "RENAME"])
    assert result.exit_code == 0
    assert "devkit batch rename" in result.stdout


def test_help_keyword_no_match_prints_hint():
    result = runner.invoke(app, ["help", "nonexistent-keyword"])
    assert result.exit_code == 0
    assert "No commands matched" in result.stdout
    assert "devkit --help" in result.stdout


def test_help_usage_signature_uses_input_output_placeholders():
    result = runner.invoke(app, ["help", "convert"])
    assert result.exit_code == 0
    # Positional file arguments are shown as "input", not each command's own metavar.
    assert "devkit convert data input --to" in result.stdout
    assert "devkit convert pdf2md input" in result.stdout
    assert "input_file" not in result.stdout
    # --output/-o is shown with the "output" placeholder, not its raw <path> metavar.
    assert "--output/-o output" in result.stdout
    assert "<path>" not in result.stdout


def test_help_usage_signature_marks_required_vs_optional():
    result = runner.invoke(app, ["help", "convert data"])
    assert result.exit_code == 0
    # --to is required: shown without brackets.
    assert "--to <json|yaml|csv>" in result.stdout
    assert "[--to" not in result.stdout
    # --flatten is an optional flag: shown in brackets with no value placeholder.
    assert "[--flatten]" in result.stdout


def test_help_usage_signature_marks_repeatable_option():
    result = runner.invoke(app, ["help", "log filter"])
    assert result.exit_code == 0
    assert "[--level <str>]..." in result.stdout


if __name__ == "__main__":
    from jiacheng_wu_devkit_114.tests import run_cov_test

    run_cov_test(
        __file__,
        "jiacheng_wu_devkit_114.cli",
        preview=False,
    )
