from dataclasses import dataclass, field
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
    temp_path = str(tmpdir)
    expected = {
        "dirname": os.path.basename(temp_path),
        "fullpath": temp_path,
        "files": {"one", "two", "three"},
        "subdirs": {}
    }
    create_dir(temp_path, expected)

    # WHEN
    actual = loaded_dir(temp_path)

    # THEN
    assert expected == actual.asdict()


@pytest.mark.dir_ctor
def test_dir_with_files_and_subdir(tmpdir):
    # GIVEN
    temp_path = str(tmpdir)
    expected = {
        "dirname": os.path.basename(temp_path),
        "fullpath": temp_path,
        "files": {"one", "two", "three"},
        "subdirs": {
            "sublevel1": {
                "dirname": "sublevel1",
                "fullpath": os.path.join(temp_path, "sublevel1"),
                "files": {"file1.txt", "file2.tsk", "file3.js"},
                "subdirs": {}
            }
        }
    }
    create_dir(temp_path, expected)

    # WHEN
    actual = loaded_dir(temp_path)

    # THEN
    assert expected == actual.asdict()


@pytest.mark.dir_ctor
def test_dir_with_multiple_subdir_levels(tmpdir):
    # GIVEN
    temp_path = str(tmpdir)
    expected = helpers.dir_schemas.multiple_subdir_levels(str(tmpdir))
    create_dir(temp_path, expected)

    # WHEN
    actual = loaded_dir(temp_path)

    # THEN
    assert expected == actual.asdict()


@pytest.fixture(scope="function")
def diff_fix(tmpdir_factory):
    src_path = tmpdir_factory.mktemp("src_dir")
    cmp_path = tmpdir_factory.mktemp("cmp_dir")

    src_dir = Dir("src_dir", str(src_path))
    cmp_dir = Dir("cmp_dir", str(cmp_path))

    yield (src_dir, cmp_dir)


def validate_diffs(left_dir: Dir,
                   right_dir: Dir,
                   expected_diff: DirDiff) -> DirDiff:
    actual_diff = sut.compare_dirs(left_dir, right_dir)

    assert expected_diff == actual_diff
    return actual_diff


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

    create_dir(src_dir.fullpath, src_dir.asdict())
    create_dir(cmp_dir.fullpath, cmp_dir.asdict())

    expected_diff = DirDiff()
    expected_diff.files = FilesDiff(missing=set(src_files), new=set(cmp_files))
    expected_diff.subdirs = SubdirDiff(missing=set(src_subdirs), new=set(cmp_subdirs))

    validate_diffs(src_dir, cmp_dir, expected_diff)


@pytest.mark.parametrize("all_diff_contents, matching_group", [
    (True, "changed"),
    (False, "shared")
])
def test_diff_only_files(diff_fix, all_diff_contents, matching_group):
    common_files = set(["common.py", "common.txt", "common.mp4"])

    src_dir, cmp_dir = diff_fix
    src_dir.files = common_files
    cmp_dir.files = common_files

    create_dir(src_dir.fullpath, src_dir.asdict(),
               all_diff_contents=all_diff_contents)
    create_dir(cmp_dir.fullpath, cmp_dir.asdict(),
               all_diff_contents=all_diff_contents)

    expected_match = {}
    expected_match[matching_group] = common_files
    expected_diff = DirDiff(files=FilesDiff(**expected_match))

    validate_diffs(src_dir, cmp_dir, expected_diff)


@pytest.mark.parametrize("all_diff_contents, matching_group", [
    (True, "changed"),
    (False, "shared")
])
def test_diff_only_subdirs(diff_fix, all_diff_contents, matching_group):
    subdir_contents = {
        sub_name: set(f"{sub_name}.file{suffix}" for suffix in [".mp4", ".jpg", ".py"])
        for sub_name in ["subdir_a", "subdir-b", "SUBDIR.C"]
    }

    src_dir, cmp_dir = diff_fix
    src_dir.subdirs = {
        d: Dir(d, os.path.join(src_dir.fullpath, d), files=files)
        for d, files in subdir_contents.items()
    }
    cmp_dir.subdirs = {
        d: Dir(d, os.path.join(cmp_dir.fullpath, d), files=files)
        for d, files in subdir_contents.items()
    }

    create_dir(src_dir.fullpath, src_dir.asdict(),
               all_diff_contents=all_diff_contents)
    create_dir(cmp_dir.fullpath, cmp_dir.asdict(),
               all_diff_contents=all_diff_contents)

    # TODO: Make this less brittle
    # Diff only cares about keys for common subdirs, so we can ignore the values
    expected_diff = DirDiff(subdirs=SubdirDiff(shared=set(subdir_contents.keys())))
    actual_diff = validate_diffs(src_dir, cmp_dir, expected_diff)

    for d in actual_diff.subdirs.shared:
        expected_match = {}
        expected_match[matching_group] = subdir_contents[d]
        expected_diff = DirDiff(files=FilesDiff(**expected_match))

        validate_diffs(src_dir.subdirs[d], cmp_dir.subdirs[d], expected_diff)


@pytest.mark.parametrize("all_diff_contents, matching_group", [
    (True, "changed"),
    (False, "shared")
])
def test_diff_nested_subdirs(diff_fix, all_diff_contents, matching_group):
    src_dir, cmp_dir = diff_fix
    common_files = set(["woah.jpg", "mad.png", "deep.arw"])

    # Nest 3 levels deep
    def init_nested_subdirs(dir_ptr):
        for i in range(1, 4):
            subdir_name = f"subdir{i}"
            dir_ptr.subdirs = {
                subdir_name: Dir(
                    subdir_name,
                    os.path.join(dir_ptr.fullpath, subdir_name)
                )
            }
            dir_ptr = dir_ptr.subdirs[subdir_name]

        # At the deepest level
        dir_ptr.files = common_files

    init_nested_subdirs(src_dir)
    init_nested_subdirs(cmp_dir)

    create_dir(src_dir.fullpath, src_dir.asdict(),
               all_diff_contents=all_diff_contents)
    create_dir(cmp_dir.fullpath, cmp_dir.asdict(),
               all_diff_contents=all_diff_contents)

    def validate_nest(src_dir: Dir, cmp_dir: Dir):
        if src_dir.subdirs and cmp_dir.subdirs:
            # Still making our way downtown
            # TODO: This also uses the assumption that validation only uses keys
            #       Find a way to make this less brittle
            common_subdir_names = set(src_dir.subdirs.keys())
            expected_diff = DirDiff(subdirs=SubdirDiff(shared=common_subdir_names))
            validate_diffs(src_dir, cmp_dir, expected_diff)

            # This should only be a single linked list of directories
            # Otherwise we're outside of the boundaries
            assert len(common_subdir_names) == 1
            subdir_name = list(common_subdir_names)[0]
            validate_nest(src_dir.subdirs[subdir_name], cmp_dir.subdirs[subdir_name])
        else:
            # Now we're in downtown
            expected_match = {}
            expected_match[matching_group] = common_files
            expected_diff = DirDiff(files=FilesDiff(**expected_match))

    validate_nest(src_dir, cmp_dir)


def test_full_diff_dirs(diff_fix):
    # GIVEN
    src_dir, cmp_dir = diff_fix
    src_dir_pattern = helpers.dir_schemas.multiple_subdir_levels(src_dir.fullpath)
    cmp_dir_pattern = helpers.dir_schemas.multiple_subdir_levels(cmp_dir.fullpath)

    create_dir(src_dir.fullpath, src_dir_pattern, all_diff_contents=True, seed="SRC")
    create_dir(cmp_dir.fullpath, cmp_dir_pattern, all_diff_contents=True, seed="CMP")

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
    assert diff.subdirs.shared
