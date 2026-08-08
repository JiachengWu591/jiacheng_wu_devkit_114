# -*- coding: utf-8 -*-

import json

from typer.testing import CliRunner

from jiacheng_wu_devkit_114.commands.log import app

runner = CliRunner()

SAMPLE_LOG = """\
2026-08-07 10:23:45 INFO Starting job
2026-08-07 10:23:46 ERROR Connection refused
Traceback (most recent call last):
ConnectionError: refused
2026-08-07 10:23:47 INFO Job finished
"""


def _write_log(tmp_path):
    p = tmp_path / "app.log"
    p.write_text(SAMPLE_LOG, encoding="utf-8")
    return p


# ------------------------------------------------------------------------------
# filter
# ------------------------------------------------------------------------------
def test_filter_help_mentions_pattern_option():
    result = runner.invoke(app, ["filter", "--help"])
    assert result.exit_code == 0
    assert "--pattern" in result.stdout


def test_filter_by_level(tmp_path):
    logfile = _write_log(tmp_path)
    result = runner.invoke(app, ["filter", str(logfile), "--level", "ERROR"])
    assert result.exit_code == 0
    assert "Connection refused" in result.stdout
    assert "Starting job" not in result.stdout


def test_filter_by_keyword_matches_traceback(tmp_path):
    logfile = _write_log(tmp_path)
    result = runner.invoke(app, ["filter", str(logfile), "--keyword", "ConnectionError"])
    assert result.exit_code == 0
    assert "Traceback" in result.stdout


def test_filter_writes_to_output_file(tmp_path):
    logfile = _write_log(tmp_path)
    dst = tmp_path / "filtered.log"
    result = runner.invoke(app, ["filter", str(logfile), "--level", "INFO", "-o", str(dst)])
    assert result.exit_code == 0
    assert dst.exists()
    assert "Starting job" in dst.read_text(encoding="utf-8")


def test_filter_missing_file_rejected():
    result = runner.invoke(app, ["filter", "does_not_exist.log"])
    assert result.exit_code != 0


# ------------------------------------------------------------------------------
# stats
# ------------------------------------------------------------------------------
def test_stats_help_mentions_json_option():
    result = runner.invoke(app, ["stats", "--help"])
    assert result.exit_code == 0
    assert "--json" in result.stdout


def test_stats_human_readable(tmp_path):
    logfile = _write_log(tmp_path)
    result = runner.invoke(app, ["stats", str(logfile)])
    assert result.exit_code == 0
    assert "ERROR: 1" in result.stdout
    assert "INFO: 2" in result.stdout


def test_stats_json_output_is_parseable(tmp_path):
    logfile = _write_log(tmp_path)
    result = runner.invoke(app, ["stats", str(logfile), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["level_counts"] == {"INFO": 2, "ERROR": 1}


def test_stats_top_n_option(tmp_path):
    logfile = _write_log(tmp_path)
    result = runner.invoke(app, ["stats", str(logfile), "--top-n", "1", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert len(payload["top_messages"]["INFO"]) <= 1


if __name__ == "__main__":
    from jiacheng_wu_devkit_114.tests import run_cov_test

    run_cov_test(
        __file__,
        "jiacheng_wu_devkit_114.commands.log",
        preview=False,
    )
