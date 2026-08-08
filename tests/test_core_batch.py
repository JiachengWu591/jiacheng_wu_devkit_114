# -*- coding: utf-8 -*-

import os
import time

import pytest

from jiacheng_wu_devkit_114.core.batch import (
    MovePlanItem,
    expand_glob,
    render_name,
    build_rename_plan,
    build_organize_plan,
    find_collisions,
    apply_plan,
)
from jiacheng_wu_devkit_114.core.errors import BatchError


# ------------------------------------------------------------------------------
# expand_glob
# ------------------------------------------------------------------------------
def test_expand_glob_matches_files_only(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "subdir").mkdir()

    result = expand_glob("*.txt", root=tmp_path)

    assert result == [tmp_path / "a.txt", tmp_path / "b.txt"]


def test_expand_glob_recursive(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (nested / "b.txt").write_text("b", encoding="utf-8")

    result = expand_glob("**/*.txt", root=tmp_path)

    assert set(result) == {tmp_path / "a.txt", nested / "b.txt"}


def test_expand_glob_no_matches_returns_empty(tmp_path):
    assert expand_glob("*.nonexistent", root=tmp_path) == []


def test_expand_glob_absolute_pattern_ignores_root(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    absolute_pattern = str(tmp_path / "*.txt")

    result = expand_glob(absolute_pattern, root=tmp_path / "unrelated")

    assert result == [tmp_path / "a.txt"]


# ------------------------------------------------------------------------------
# render_name
# ------------------------------------------------------------------------------
def test_render_name_seq_padding(tmp_path):
    path = tmp_path / "photo.jpg"
    assert render_name("{stem}_{seq:03d}{ext}", seq=7, path=path) == "photo_007.jpg"


def test_render_name_name_and_parent(tmp_path):
    path = tmp_path / "sub" / "photo.jpg"
    assert render_name("{parent}-{name}", seq=1, path=path) == "sub-photo.jpg"


def test_render_name_no_ext(tmp_path):
    path = tmp_path / "README"
    assert render_name("{stem}{ext}", seq=1, path=path) == "README"


def test_render_name_unknown_field_raises(tmp_path):
    with pytest.raises(BatchError):
        render_name("{unknown_field}", seq=1, path=tmp_path / "a.txt")


def test_render_name_malformed_template_raises(tmp_path):
    with pytest.raises(BatchError):
        render_name("{stem", seq=1, path=tmp_path / "a.txt")


# ------------------------------------------------------------------------------
# build_rename_plan
# ------------------------------------------------------------------------------
def test_build_rename_plan_same_directory(tmp_path):
    paths = [tmp_path / "a.txt", tmp_path / "b.txt"]
    plan = build_rename_plan(paths, "{stem}_{seq:02d}{ext}")

    assert plan == [
        MovePlanItem(src=tmp_path / "a.txt", dst=tmp_path / "a_01.txt"),
        MovePlanItem(src=tmp_path / "b.txt", dst=tmp_path / "b_02.txt"),
    ]


def test_build_rename_plan_does_not_touch_filesystem(tmp_path):
    src = tmp_path / "a.txt"
    src.write_text("hello", encoding="utf-8")
    build_rename_plan([src], "{stem}_new{ext}")
    assert src.exists()
    assert not (tmp_path / "a_new.txt").exists()


# ------------------------------------------------------------------------------
# build_organize_plan
# ------------------------------------------------------------------------------
def test_build_organize_plan_by_ext(tmp_path):
    dest = tmp_path / "organized"
    paths = [tmp_path / "a.jpg", tmp_path / "b.PDF", tmp_path / "c"]
    plan = build_organize_plan(paths, by="ext", dest_root=dest)

    assert plan == [
        MovePlanItem(src=tmp_path / "a.jpg", dst=dest / "jpg" / "a.jpg"),
        MovePlanItem(src=tmp_path / "b.PDF", dst=dest / "pdf" / "b.PDF"),
        MovePlanItem(src=tmp_path / "c", dst=dest / "no_ext" / "c"),
    ]


def test_build_organize_plan_by_mtime(tmp_path):
    src = tmp_path / "a.txt"
    src.write_text("hello", encoding="utf-8")
    dest = tmp_path / "organized"

    plan = build_organize_plan([src], by="mtime", dest_root=dest, date_format="%Y-%m")

    expected_bucket = time.strftime("%Y-%m", time.localtime(os.path.getmtime(src)))
    assert plan == [MovePlanItem(src=src, dst=dest / expected_bucket / "a.txt")]


def test_build_organize_plan_invalid_by_raises(tmp_path):
    with pytest.raises(BatchError):
        build_organize_plan([tmp_path / "a.txt"], by="size", dest_root=tmp_path / "out")


# ------------------------------------------------------------------------------
# find_collisions
# ------------------------------------------------------------------------------
def test_find_collisions_duplicate_targets(tmp_path):
    plan = [
        MovePlanItem(src=tmp_path / "a.txt", dst=tmp_path / "x.txt"),
        MovePlanItem(src=tmp_path / "b.txt", dst=tmp_path / "x.txt"),
    ]
    assert find_collisions(plan) == [tmp_path / "x.txt"]


def test_find_collisions_target_exists_outside_plan(tmp_path):
    existing = tmp_path / "x.txt"
    existing.write_text("already here", encoding="utf-8")
    plan = [MovePlanItem(src=tmp_path / "a.txt", dst=existing)]
    assert find_collisions(plan) == [existing]


def test_find_collisions_no_conflict_when_clean(tmp_path):
    plan = [
        MovePlanItem(src=tmp_path / "a.txt", dst=tmp_path / "a_new.txt"),
        MovePlanItem(src=tmp_path / "b.txt", dst=tmp_path / "b_new.txt"),
    ]
    assert find_collisions(plan) == []


def test_find_collisions_self_rename_not_flagged(tmp_path):
    # dst happens to equal src (e.g. template is a no-op) — that file legitimately
    # exists already, but it's the item's own source, not a foreign collision.
    existing = tmp_path / "a.txt"
    existing.write_text("hi", encoding="utf-8")
    plan = [MovePlanItem(src=existing, dst=existing)]
    assert find_collisions(plan) == []


# ------------------------------------------------------------------------------
# apply_plan
# ------------------------------------------------------------------------------
def test_apply_plan_renames_files(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("hello", encoding="utf-8")
    plan = [MovePlanItem(src=a, dst=tmp_path / "a_new.txt")]

    applied = apply_plan(plan)

    assert not a.exists()
    assert (tmp_path / "a_new.txt").read_text(encoding="utf-8") == "hello"
    assert applied == plan


def test_apply_plan_creates_parent_dirs(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("hello", encoding="utf-8")
    dst = tmp_path / "sub" / "dir" / "a.txt"
    plan = [MovePlanItem(src=a, dst=dst)]

    apply_plan(plan)

    assert dst.exists()


def test_apply_plan_refuses_and_touches_nothing_on_collision(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("A", encoding="utf-8")
    b.write_text("B", encoding="utf-8")
    plan = [
        MovePlanItem(src=a, dst=tmp_path / "x.txt"),
        MovePlanItem(src=b, dst=tmp_path / "x.txt"),
    ]

    with pytest.raises(BatchError):
        apply_plan(plan)

    # Nothing was touched: both original files still exist untouched.
    assert a.exists()
    assert b.exists()
    assert not (tmp_path / "x.txt").exists()


def test_apply_plan_overwrite_true_bypasses_collision_check(tmp_path):
    a = tmp_path / "a.txt"
    existing = tmp_path / "x.txt"
    a.write_text("new content", encoding="utf-8")
    existing.write_text("old content", encoding="utf-8")
    plan = [MovePlanItem(src=a, dst=existing)]

    apply_plan(plan, overwrite=True)

    assert existing.read_text(encoding="utf-8") == "new content"


if __name__ == "__main__":
    from jiacheng_wu_devkit_114.tests import run_cov_test

    run_cov_test(
        __file__,
        "jiacheng_wu_devkit_114.core.batch",
        preview=False,
    )
