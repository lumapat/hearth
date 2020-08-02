from typing import Any, Dict
from pathlib import Path
import os

import pytest

from hearth.dirdiff import Dir, loaded_dir
import hearth.dirdiff as sut


def create_dir(path: str,
               dir_dict: Dict[str, Any],
               all_diff_contents: bool = False) -> None:
    """ Creates a directory in the specified path

    :param path: Path to create directory in
    :param dir_dict: Specification of contents to create in directory
    """

    for f in dir_dict["files"]:
        fp = Path(os.path.join(path, f))
        if all_diff_contents:
            fp.write_text(str(fp))
        else:
            fp.touch()

    for contents in dir_dict["subdirs"]:
        subdir_path = os.path.join(path, contents["dirname"])
        Path(subdir_path).mkdir()

        create_dir(subdir_path, contents, all_diff_contents=all_diff_contents)


@pytest.mark.dir_ctor
def test_dir_with_only_files(tmpdir):
    # GIVEN
    temp_path = str(tmpdir)
    expected = {
        "dirname": os.path.basename(temp_path),
        "fullpath": temp_path,
        "files": {"one", "two", "three"},
        "subdirs": []
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
        "subdirs": [{
            "dirname": "sublevel1",
            "fullpath": os.path.join(temp_path, "sublevel1"),
            "files": {"file1.txt", "file2.tsk", "file3.js"},
            "subdirs": []
        }]
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
    expected = {
        "dirname": os.path.basename(temp_path),
        "fullpath": temp_path,
        "files": {"one"},
        "subdirs": [{
            "dirname": "sublevel1",
            "fullpath": os.path.join(temp_path, "sublevel1"),
            "files": {"file1.txt", "file2.tsk"},
            "subdirs": [{
                "dirname": "sublevel2",
                "fullpath": os.path.join(temp_path, "sublevel1", "sublevel2"),
                "files": {"ugh.js", "ayy.css", "nope.html"},
                "subdirs": [{
                    "dirname": "Secret Pictures",
                    "fullpath": os.path.join(temp_path, "sublevel1", "sublevel2", "Secret Pictures"),
                    "files": {"SECRET.png"},
                    "subdirs": []
                }]
            },
            {
                "dirname": "Pictures",
                "fullpath": os.path.join(temp_path, "sublevel1", "Pictures"),
                "files": {"img1.jpg", "img2.jpg", "vid1.mp4"},
                "subdirs": []
            }]
        }]
    }
    create_dir(temp_path, expected)

    # WHEN
    actual = loaded_dir(temp_path)

    # THEN
    assert expected == actual.asdict()


@pytest.fixture(scope="function")
def diff_fix(tmpdir_factory):
    left_path = tmpdir_factory.mktemp("left_dir")
    right_path = tmpdir_factory.mktemp("right_dir")

    left_dir = Dir("left_dir", str(left_path), set(), [])
    right_dir = Dir("right_dir", str(right_path), set(), [])

    yield (left_dir, right_dir)


@pytest.mark.parametrize("left_files, right_files, left_subdirs, right_subdirs", [
    (["f.txt", "g.txt"], [], [], []),
    ([], ["f.txt", "g.txt"], [], []),
    (["a.tsk", "b.cpp"], ["f.png", "g.md"], [], []),
    ([], [], ["subdir_a", "subdir_b"], []),
    ([], [], [], ["subdir_a", "subdir_b"]),
    ([], [], ["subdir_a", "subdir_b"], ["subdir_c", "subdir_d"]),
    (["a.tsk", "b.cpp"], ["f.png", "g.md"], ["subdir_a", "subdir_b"], ["subdir_c", "subdir_d"])
])
def test_diff_shallow_with_no_common_items(diff_fix,
                                           left_files,
                                           right_files,
                                           left_subdirs,
                                           right_subdirs) -> None:
    left_dir, right_dir = diff_fix

    left_dir.files = set(left_files)
    right_dir.files = set(right_files)

    left_dir.subdirs = [Dir(d, os.path.join(left_dir.fullpath, d), {}, []) for d in left_subdirs]
    right_dir.subdirs = [Dir(d, os.path.join(right_dir.fullpath, d), {}, []) for d in right_subdirs]

    create_dir(left_dir.fullpath, left_dir.asdict())
    create_dir(right_dir.fullpath, right_dir.asdict())

    actual_left_files, actual_right_files, actual_common = sut.compare_files(left_dir, right_dir)

    assert set(left_files) == actual_left_files
    assert set(right_files) == actual_right_files
    assert not actual_common

    assert set(left_subdirs) == sut.left_dirs_only(left_dir, right_dir)
    assert set(right_subdirs) == sut.right_dirs_only(left_dir, right_dir)


def test_diff_common_files_with_diff_contents(diff_fix):
    common_files = set(["common.py", "common.txt", "common.mp4"])

    left_dir, right_dir = diff_fix
    left_dir.files = common_files
    right_dir.files = common_files

    create_dir(left_dir.fullpath, left_dir.asdict(), all_diff_contents=True)
    create_dir(right_dir.fullpath, right_dir.asdict(), all_diff_contents=True)

    actual_left_files, actual_right_files, actual_common = sut.compare_files(left_dir, right_dir)

    assert common_files == actual_left_files
    assert common_files == actual_right_files
    assert not actual_common

    assert not sut.left_dirs_only(left_dir, right_dir)
    assert not sut.right_dirs_only(left_dir, right_dir)


def test_diff_common_files_with_same_contents(diff_fix):
    common_files = set(["common.py", "common.txt", "common.mp4"])

    left_dir, right_dir = diff_fix
    left_dir.files = common_files
    right_dir.files = common_files

    create_dir(left_dir.fullpath, left_dir.asdict(), all_diff_contents=False)
    create_dir(right_dir.fullpath, right_dir.asdict(), all_diff_contents=False)

    actual_left_files, actual_right_files, actual_common = sut.compare_files(left_dir, right_dir)

    assert not actual_left_files
    assert not actual_right_files
    assert common_files == actual_common

    assert not sut.left_dirs_only(left_dir, right_dir)
    assert not sut.right_dirs_only(left_dir, right_dir)


def test_diff_common_subdirs_with_diffs(diff_fix):
    common_subdir_names = ["subdir_a", "subdir-b", "SUBDIR.C"]
    file_suffixes = [".mp4", ".jpg", ".py"]

    left_dir, right_dir = diff_fix

    left_dir.subdirs = [
        Dir(d,
            os.path.join(left_dir.fullpath, d),
            set(f"{d}{suffix}" for suffix in file_suffixes),
            [])
        for d in common_subdir_names]
    right_dir.subdirs = [
        Dir(d,
            os.path.join(right_dir.fullpath, d),
            set(f"{d}{suffix}" for suffix in file_suffixes),
            [])
        for d in common_subdir_names]

    create_dir(left_dir.fullpath, left_dir.asdict(), all_diff_contents=True)
    create_dir(right_dir.fullpath, right_dir.asdict(), all_diff_contents=True)

    actual_left_files, actual_right_files, actual_common = sut.compare_files(left_dir, right_dir)

    assert not actual_left_files
    assert not actual_right_files
    assert not actual_common

    assert not sut.left_dirs_only(left_dir, right_dir)
    assert not sut.right_dirs_only(left_dir, right_dir)

    common_subdirs = sut.common_dirs(left_dir, right_dir)

    for d, contents in common_subdirs.items():
        assert not contents[0].subdirs
        assert not contents[1].subdirs

        # TODO: Make an actual expected value for this test
        actual_left_files, actual_right_files, actual_common = sut.compare_files(contents[0], contents[1])
        assert actual_left_files
        assert actual_right_files
        assert not actual_common


def test_diff_common_subdirs_with_same_contents(diff_fix):
    common_subdir_names = ["subdir_a", "subdir-b", "SUBDIR.C"]
    file_suffixes = [".mp4", ".jpg", ".py"]

    left_dir, right_dir = diff_fix

    left_dir.subdirs = [
        Dir(d,
            os.path.join(left_dir.fullpath, d),
            set(f"{d}{suffix}" for suffix in file_suffixes),
            [])
        for d in common_subdir_names]
    right_dir.subdirs = [
        Dir(d,
            os.path.join(right_dir.fullpath, d),
            set(f"{d}{suffix}" for suffix in file_suffixes),
            [])
        for d in common_subdir_names]

    create_dir(left_dir.fullpath, left_dir.asdict(), all_diff_contents=False)
    create_dir(right_dir.fullpath, right_dir.asdict(), all_diff_contents=False)

    # TODO: Make these names better and consistent?
    actual_left_files, actual_right_files, actual_common = sut.compare_files(left_dir, right_dir)

    assert not actual_left_files
    assert not actual_right_files
    assert not actual_common

    assert not sut.left_dirs_only(left_dir, right_dir)
    assert not sut.right_dirs_only(left_dir, right_dir)

    common_subdirs = sut.common_dirs(left_dir, right_dir)

    for d, contents in common_subdirs.items():
        assert not contents[0].subdirs
        assert not contents[1].subdirs

        actual_left_files, actual_right_files, files_in_both = sut.compare_files(contents[0], contents[1])

        assert not actual_left_files
        assert not actual_right_files

        assert contents[0].files == files_in_both
        assert contents[1].files == files_in_both


# def test_diff_deep_subdir_tree_with_diffs(diff_fix):
#     left_dir, right_dir = diff_fix


# TEST CASES:
#  - Mix of common files, common subdirs, diff files, diff subdirs (1 sublevel)
#  - Deep subdir level (3) with diffs
#  - Deep subdir level (3) without diffs