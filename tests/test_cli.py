# -*- coding: utf-8 -*-

from typer.testing import CliRunner

from jiacheng_wu_devkit_114.cli import app

runner = CliRunner()


def test_top_level_help_lists_three_groups():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for name in ("convert", "batch", "log"):
        assert name in result.stdout


def test_convert_group_reachable_from_top_level():
    result = runner.invoke(app, ["convert", "--help"])
    assert result.exit_code == 0
    assert "pdf2md" in result.stdout


def test_batch_group_reachable_from_top_level():
    result = runner.invoke(app, ["batch", "--help"])
    assert result.exit_code == 0
    assert "rename" in result.stdout
    assert "organize" in result.stdout


def test_log_group_reachable_from_top_level():
    result = runner.invoke(app, ["log", "--help"])
    assert result.exit_code == 0
    assert "filter" in result.stdout
    assert "stats" in result.stdout


if __name__ == "__main__":
    from jiacheng_wu_devkit_114.tests import run_cov_test

    run_cov_test(
        __file__,
        "jiacheng_wu_devkit_114.cli",
        preview=False,
    )
