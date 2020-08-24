from dataclasses import dataclass, field
from os import fspath
from pathlib import Path
from typing import Any, Dict, Set
import os

import pytest  # type: ignore

from hearth.dirdiff import (
    Dir,
    DirDiff,
    FilesDiff,
    SubdirDiff,
    loaded_dir
)
from helpers.dir_schemas import create_dir
import hearth.dirdiff as sut
import helpers.dir_schemas


@pytest.mark.dir_ctor
def test_dir_with_only_files(tmpdir):
    # GIVEN
    temp_path = Path(tmpdir)
    expected = Dir(
        temp_path.name,
        fspath(temp_path),
        {"one", "two", "three"}
    )
    create_dir(temp_path, expected)

    # WHEN
    actual = loaded_dir(temp_path)

    # THEN
    assert expected == actual


@pytest.mark.dir_ctor
def test_dir_with_files_and_subdir(tmpdir):
    # GIVEN
    temp_path = Path(tmpdir)
    expected = Dir(
        temp_path.name,
        fspath(temp_path),
        {"one", "two", "three"}
    )
    expected.subdirs = {
        "sublevel1": Dir(
            "sublevel1",
            fspath(temp_path/"sublevel1"),
            {"file1.txt", "file2.tsk", "file3.js"},
        )
    }

    create_dir(temp_path, expected)

    # WHEN
    actual = loaded_dir(temp_path)

    # THEN
    assert expected == actual


@pytest.mark.dir_ctor
def test_dir_with_multiple_subdir_levels(tmpdir):
    # GIVEN
    temp_path = Path(tmpdir)
    expected = helpers.dir_schemas.multiple_subdir_levels(str(temp_path))
    create_dir(temp_path, expected)

    # WHEN
    actual = loaded_dir(temp_path)

    # THEN
    assert expected == actual


@pytest.fixture(scope="function")
def diff_fix(tmpdir_factory):
    src_path = tmpdir_factory.mktemp("src_dir")
    cmp_path = tmpdir_factory.mktemp("cmp_dir")

    src_dir = Dir("src_dir", str(src_path))
    cmp_dir = Dir("cmp_dir", str(cmp_path))

    yield (src_dir, cmp_dir)


@pytest.mark.parametrize("src_files, cmp_files, src_subdirs, cmp_subdirs", [
    (["f.txt", "g.txt"], [], [], []),
    ([], ["f.txt", "g.txt"], [], []),
    (["a.tsk", "b.cpp"], ["f.png", "g.md"], [], []),
    ([], [], ["subdir_a", "subdir_b"], []),
    ([], [], [], ["subdir_a", "subdir_b"]),
    ([], [], ["subdir_a", "subdir_b"], ["subdir_c", "subdir_d"]),
    (["a.tsk", "b.cpp"], ["f.png", "g.md"], [
     "subdir_a", "subdir_b"], ["subdir_c", "subdir_d"])
])
def test_diff_shallow_with_no_common_items(diff_fix,
                                           src_files,
                                           cmp_files,
                                           src_subdirs,
                                           cmp_subdirs) -> None:
    src_dir, cmp_dir = diff_fix

    src_dir.files = set(src_files)
    cmp_dir.files = set(cmp_files)

    src_dir.subdirs = {
        d: Dir(d, os.path.join(src_dir.fullpath, d)) for d in src_subdirs}
    cmp_dir.subdirs = {
        d: Dir(d, os.path.join(cmp_dir.fullpath, d)) for d in cmp_subdirs}

    create_dir(src_dir.fullpath, src_dir)
    create_dir(cmp_dir.fullpath, cmp_dir)

    expected = DirDiff()
    expected.files = FilesDiff(missing=set(src_files), new=set(cmp_files))
    expected.subdirs = SubdirDiff(missing=set(src_subdirs), new=set(cmp_subdirs))

    assert expected == sut.full_diff_dirs(src_dir, cmp_dir)


@pytest.mark.parametrize("empty_files, matching_group", [
    (False, "changed"),
    (True, "shared")
])
def test_diff_only_files(diff_fix, empty_files, matching_group):
    common_files = set(["common.py", "common.txt", "common.mp4"])

    src_dir, cmp_dir = diff_fix
    src_dir.files = common_files
    cmp_dir.files = common_files

    create_dir(src_dir.fullpath, src_dir,
               empty_files=empty_files)
    create_dir(cmp_dir.fullpath, cmp_dir,
               empty_files=empty_files)

    expected_match = {}
    expected_match[matching_group] = common_files
    expected = DirDiff(files=FilesDiff(**expected_match))

    assert expected == sut.full_diff_dirs(src_dir, cmp_dir)


def test_diff_only_subdirs_same_contents(diff_fix):
    subdir_names = {"subdir_a", "subdir-b", "SUBDIR.C"}
    subdir_contents = {
        sub_name: set(f"{sub_name}.file{suffix}" for suffix in [".mp4", ".jpg", ".py"])
        for sub_name in subdir_names
    }

    src_dir, cmp_dir = diff_fix
    src_dir.subdirs = {
        d: Dir(d, Path(src_dir.fullpath)/d, files=files)
        for d, files in subdir_contents.items()
    }
    cmp_dir.subdirs = {
        d: Dir(d, Path(cmp_dir.fullpath)/d, files=files)
        for d, files in subdir_contents.items()
    }

    create_dir(src_dir.fullpath, src_dir, empty_files=True)
    create_dir(cmp_dir.fullpath, cmp_dir, empty_files=True)

    expected = DirDiff(subdirs=SubdirDiff(shared=subdir_names))
    assert expected == sut.full_diff_dirs(src_dir, cmp_dir)


def test_diff_only_subdirs_diff_contents(diff_fix):
    subdir_names = {"subdir_a", "subdir-b", "SUBDIR.C"}
    subdir_contents = {
        sub_name: set(f"{sub_name}.file{suffix}" for suffix in [".mp4", ".jpg", ".py"])
        for sub_name in subdir_names
    }

    src_dir, cmp_dir = diff_fix
    src_dir.subdirs = {
        d: Dir(d, Path(src_dir.fullpath)/d, files=files)
        for d, files in subdir_contents.items()
    }
    cmp_dir.subdirs = {
        d: Dir(d, Path(cmp_dir.fullpath)/d, files=files)
        for d, files in subdir_contents.items()
    }

    create_dir(src_dir.fullpath, src_dir, empty_files=False, seed="SRC")
    create_dir(cmp_dir.fullpath, cmp_dir, empty_files=False, seed="CMP")

    # Add relative path to filenames
    enriched_filenames = {
        f"{subdir}/{filename}"
        for subdir in subdir_names
        for filename in subdir_contents[subdir]
    }

    expected = DirDiff(files=FilesDiff(changed=enriched_filenames))
    assert expected == sut.full_diff_dirs(src_dir, cmp_dir)


def test_diff_nested_subdirs_same_contents(diff_fix):
    src_dir, cmp_dir = diff_fix
    common_files = set(["woah.jpg", "mad.png", "deep.arw"])

    src_dir = helpers.dir_schemas.deeply_nested_subdirs(src_dir.fullpath, common_files)
    cmp_dir = helpers.dir_schemas.deeply_nested_subdirs(cmp_dir.fullpath, common_files)

    create_dir(src_dir.fullpath, src_dir, empty_files=True)
    create_dir(cmp_dir.fullpath, cmp_dir, empty_files=True)

    expected = DirDiff()
    expected.subdirs = SubdirDiff(shared={"subdir1"})

    assert expected == sut.full_diff_dirs(src_dir, cmp_dir)


def test_diff_nested_subdirs_diff_contents(diff_fix):
    src_dir, cmp_dir = diff_fix
    common_files = set(["woah.jpg", "mad.png", "deep.arw"])

    src_dir = helpers.dir_schemas.deeply_nested_subdirs(src_dir.fullpath, common_files)
    cmp_dir = helpers.dir_schemas.deeply_nested_subdirs(cmp_dir.fullpath, common_files)

    create_dir(src_dir.fullpath, src_dir, empty_files=False, seed="SRC")
    create_dir(cmp_dir.fullpath, cmp_dir, empty_files=False, seed="CMP")

    expected = DirDiff()
    prefix = "subdir1/subdir2/subdir3/"
    expected.files = FilesDiff(changed={prefix+p for p in common_files})

    assert expected == sut.full_diff_dirs(src_dir, cmp_dir)


def test_full_diff_dirs(diff_fix):
    # GIVEN
    src_dir, cmp_dir = diff_fix
    src_dir = helpers.dir_schemas.multiple_subdir_levels(src_dir.fullpath)
    cmp_dir = helpers.dir_schemas.multiple_subdir_levels(cmp_dir.fullpath)

    create_dir(src_dir.fullpath, src_dir, empty_files=False, seed="SRC")
    create_dir(cmp_dir.fullpath, cmp_dir, empty_files=False, seed="CMP")

    # WHEN
    src_dir = loaded_dir(src_dir.fullpath)
    cmp_dir = loaded_dir(cmp_dir.fullpath)

    diff = sut.full_diff_dirs(src_dir, cmp_dir)

    # THEN
    assert diff.files.changed
    assert not diff.files.missing
    assert not diff.files.new
    assert not diff.files.shared

    assert not diff.subdirs.missing
    assert not diff.subdirs.new
    assert not diff.subdirs.shared


# TODO: Redo tests for dirdiff to use full_dir_diff
# TODO: Add tests for different diff cases
# TODO: Add sync tests as well as sync strategies