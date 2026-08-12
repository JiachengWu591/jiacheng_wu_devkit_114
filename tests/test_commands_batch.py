# -*- coding: utf-8 -*-

from typer.testing import CliRunner

from jiacheng_wu_devkit_114.commands.batch import app

runner = CliRunner()

# windows_expand_args=False: CliRunner routes through Click's main() same as real usage,
# so glob-pattern args (containing '*') would otherwise get pre-expanded by Click on
# Windows before our command sees them—see the comment in cli.py's main() for why.
INVOKE_KW = {"windows_expand_args": False}


# ------------------------------------------------------------------------------
# rename
# ------------------------------------------------------------------------------
def test_rename_help_mentions_dry_run_and_yes():
    result = runner.invoke(app, ["rename", "--help"], **INVOKE_KW)
    assert result.exit_code == 0
    assert "--dry-run" in result.stdout
    assert "--yes" in result.stdout


def test_rename_dry_run_does_not_touch_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")

    result = runner.invoke(app, ["rename", "*.txt", "--template", "{stem}_new{ext}", "--dry-run"], **INVOKE_KW)

    assert result.exit_code == 0
    assert (tmp_path / "a.txt").exists()
    assert not (tmp_path / "a_new.txt").exists()


def test_rename_declined_confirmation_leaves_files_untouched(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")

    result = runner.invoke(app, ["rename", "*.txt", "--template", "{stem}_new{ext}"], input="n\n", **INVOKE_KW)

    assert (tmp_path / "a.txt").exists()
    assert not (tmp_path / "a_new.txt").exists()


def test_rename_with_yes_applies(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")

    result = runner.invoke(app, ["rename", "*.txt", "--template", "{stem}_new{ext}", "--yes"], **INVOKE_KW)

    assert result.exit_code == 0
    assert not (tmp_path / "a.txt").exists()
    assert (tmp_path / "a_new.txt").read_text(encoding="utf-8") == "hello"


def test_rename_no_matches_exits_cleanly(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["rename", "*.nonexistent", "--template", "{name}"], **INVOKE_KW)

    assert result.exit_code == 0
    assert "No files matched" in result.output


def test_rename_collision_refuses_and_touches_nothing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")

    result = runner.invoke(app, ["rename", "*.txt", "--template", "same{ext}", "--yes"], **INVOKE_KW)

    assert result.exit_code == 1
    assert (tmp_path / "a.txt").exists()
    assert (tmp_path / "b.txt").exists()
    assert not (tmp_path / "same.txt").exists()


def test_rename_dry_run_also_detects_collision(tmp_path, monkeypatch):
    # --dry-run must be a trustworthy preview: a plan that would be rejected for real must
    # also be rejected (with a non-zero exit) under --dry-run, not silently look clean.
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")

    result = runner.invoke(app, ["rename", "*.txt", "--template", "same{ext}", "--dry-run"], **INVOKE_KW)

    assert result.exit_code == 1
    assert "would conflict" in result.output
    assert (tmp_path / "a.txt").exists()
    assert (tmp_path / "b.txt").exists()
    assert not (tmp_path / "same.txt").exists()


# ------------------------------------------------------------------------------
# organize
# ------------------------------------------------------------------------------
def test_organize_help_mentions_by_option():
    result = runner.invoke(app, ["organize", "--help"])
    assert result.exit_code == 0
    assert "--by" in result.stdout


def test_organize_dry_run_does_not_touch_files(tmp_path):
    (tmp_path / "a.jpg").write_text("a", encoding="utf-8")

    result = runner.invoke(app, ["organize", str(tmp_path), "--by", "ext", "--dry-run"])

    assert result.exit_code == 0
    assert (tmp_path / "a.jpg").exists()
    assert not (tmp_path / "jpg").exists()


def test_organize_with_yes_moves_files(tmp_path):
    (tmp_path / "a.jpg").write_text("a", encoding="utf-8")

    result = runner.invoke(app, ["organize", str(tmp_path), "--by", "ext", "--yes"])

    assert result.exit_code == 0
    assert (tmp_path / "jpg" / "a.jpg").exists()
    assert not (tmp_path / "a.jpg").exists()


def test_organize_collision_refuses_and_touches_nothing(tmp_path):
    (tmp_path / "a.jpg").write_text("a", encoding="utf-8")
    # Pre-create the destination this move would land on, with unrelated content.
    (tmp_path / "jpg").mkdir()
    (tmp_path / "jpg" / "a.jpg").write_text("pre-existing", encoding="utf-8")

    result = runner.invoke(app, ["organize", str(tmp_path), "--by", "ext", "--yes"])

    assert result.exit_code == 1
    assert (tmp_path / "a.jpg").read_text(encoding="utf-8") == "a"
    assert (tmp_path / "jpg" / "a.jpg").read_text(encoding="utf-8") == "pre-existing"


def test_organize_dry_run_also_detects_collision(tmp_path):
    # Same guarantee as rename: --dry-run must surface a collision that the real run would
    # hit, not just print a plan that later turns out to be rejected.
    (tmp_path / "a.jpg").write_text("a", encoding="utf-8")
    (tmp_path / "jpg").mkdir()
    (tmp_path / "jpg" / "a.jpg").write_text("pre-existing", encoding="utf-8")

    result = runner.invoke(app, ["organize", str(tmp_path), "--by", "ext", "--dry-run"])

    assert result.exit_code == 1
    assert "would conflict" in result.output
    assert (tmp_path / "a.jpg").read_text(encoding="utf-8") == "a"
    assert (tmp_path / "jpg" / "a.jpg").read_text(encoding="utf-8") == "pre-existing"


def test_organize_no_files_message(tmp_path):
    result = runner.invoke(app, ["organize", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "No files found" in result.output


if __name__ == "__main__":
    from jiacheng_wu_devkit_114.tests import run_cov_test

    run_cov_test(
        __file__,
        "jiacheng_wu_devkit_114.commands.batch",
        preview=False,
    )
