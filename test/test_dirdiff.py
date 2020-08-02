from dataclasses import dataclass, field
from typing import Any, Dict, Set
from pathlib import Path
import os

import pytest # type: ignore

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


@dataclass
class DiffResult:
    left_files: Set[str] = field(default_factory=set)
    right_files: Set[str] = field(default_factory=set)
    common_files: Set[str] = field(default_factory=set)

    left_subdirs: Set[str] = field(default_factory=set)
    right_subdirs: Set[str] = field(default_factory=set)
    common_subdirs: Dict[str, Dir] = field(default_factory=dict)


def validate_diffs(left_dir: Dir,
                   right_dir: Dir,
                   expected_diff: DiffResult) -> DiffResult:
    actual_file_cmp = sut.compare_files(left_dir, right_dir)
    actual_subdir_cmp = sut.compare_subdirs(left_dir, right_dir)

    actual_diff = DiffResult(
        left_files=actual_file_cmp[0],
        right_files=actual_file_cmp[1],
        common_files=actual_file_cmp[2],
        left_subdirs=actual_subdir_cmp[0],
        right_subdirs=actual_subdir_cmp[1],
        common_subdirs=actual_subdir_cmp[2] # type: ignore
    )

    assert expected_diff.left_files == actual_diff.left_files
    assert expected_diff.right_files == actual_diff.right_files
    assert expected_diff.common_files == actual_diff.common_files

    assert expected_diff.left_subdirs == actual_diff.left_subdirs
    assert expected_diff.right_subdirs == actual_diff.right_subdirs
    assert expected_diff.common_subdirs.keys() == actual_diff.common_subdirs.keys()

    return actual_diff


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

    left_dir.subdirs = [Dir(d, os.path.join(left_dir.fullpath, d), set(), []) for d in left_subdirs]
    right_dir.subdirs = [Dir(d, os.path.join(right_dir.fullpath, d), set(), []) for d in right_subdirs]

    create_dir(left_dir.fullpath, left_dir.asdict())
    create_dir(right_dir.fullpath, right_dir.asdict())

    expected_diff = DiffResult()
    expected_diff.left_files = set(left_files)
    expected_diff.right_files = set(right_files)
    expected_diff.left_subdirs = set(left_subdirs)
    expected_diff.right_subdirs = set(right_subdirs)

    validate_diffs(left_dir, right_dir, expected_diff)


@pytest.mark.parametrize("all_diff_contents, matching_groups", [
    (True, ["left_files", "right_files"]),
    (False, ["common_files"])
])
def test_diff_only_files(diff_fix, all_diff_contents, matching_groups):
    common_files = set(["common.py", "common.txt", "common.mp4"])

    left_dir, right_dir = diff_fix
    left_dir.files = common_files
    right_dir.files = common_files

    create_dir(left_dir.fullpath, left_dir.asdict(), all_diff_contents=all_diff_contents)
    create_dir(right_dir.fullpath, right_dir.asdict(), all_diff_contents=all_diff_contents)

    expected_matches = {
        group: common_files
        for group in matching_groups
    }
    expected_diff = DiffResult(**expected_matches)

    validate_diffs(left_dir, right_dir, expected_diff)


@pytest.mark.parametrize("all_diff_contents, matching_groups", [
    (True, ["left_files", "right_files"]),
    (False, ["common_files"])
])
def test_diff_only_subdirs(diff_fix, all_diff_contents, matching_groups):
    subdir_contents = {
        sub_name: set(f"{sub_name}.file{suffix}" for suffix in [".mp4", ".jpg", ".py"])
        for sub_name in ["subdir_a", "subdir-b", "SUBDIR.C"]
    }

    left_dir, right_dir = diff_fix
    left_dir.subdirs = [
        Dir(d, os.path.join(left_dir.fullpath, d), files, [])
        for d, files in subdir_contents.items()
    ]
    right_dir.subdirs = [
        Dir(d, os.path.join(right_dir.fullpath, d), files, [])
        for d, files in subdir_contents.items()
    ]

    create_dir(left_dir.fullpath, left_dir.asdict(), all_diff_contents=all_diff_contents)
    create_dir(right_dir.fullpath, right_dir.asdict(), all_diff_contents=all_diff_contents)

    # Diff only cares about keys for common subdirs, so we can ignore the values
    expected_diff = DiffResult(common_subdirs=subdir_contents)
    actual_diff = validate_diffs(left_dir, right_dir, expected_diff)

    for d, contents in actual_diff.common_subdirs.items():
        expected_matches = {
            group: subdir_contents[d]
            for group in matching_groups
        }
        expected_diff = DiffResult(**expected_matches)

        validate_diffs(contents[0], contents[1], expected_diff)


@pytest.mark.parametrize("all_diff_contents, matching_groups", [
    (True, ["left_files", "right_files"]),
    (False, ["common_files"])
])
def test_diff_nested_subdirs(diff_fix, all_diff_contents, matching_groups):
    left_dir, right_dir = diff_fix
    common_files = set(["woah.jpg", "mad.png", "deep.arw"])

    # Nest 3 levels deep
    def init_nested_subdirs(dir_ptr):
        for i in range(1,4):
            subdir_name = f"subdir{i}"
            dir_ptr.subdirs = [Dir(
                subdir_name,
                os.path.join(dir_ptr.fullpath, subdir_name),
                set(),
                []
            )]
            dir_ptr = dir_ptr.subdirs[0]

        # At the deepest level
        dir_ptr.files = common_files

    init_nested_subdirs(left_dir)
    init_nested_subdirs(right_dir)

    create_dir(left_dir.fullpath, left_dir.asdict(), all_diff_contents=all_diff_contents)
    create_dir(right_dir.fullpath, right_dir.asdict(), all_diff_contents=all_diff_contents)

    def validate_nest(left_dir: Dir, right_dir: Dir):
        if left_dir.subdirs and right_dir.subdirs:
            # Still making our way downtown
            common_subdirs = {d.dirname: d for d in left_dir.subdirs}
            expected_diff = DiffResult(common_subdirs=common_subdirs)
            validate_diffs(left_dir, right_dir, expected_diff)

            assert len(common_subdirs.keys()) == 1
            validate_nest(left_dir.subdirs[0], right_dir.subdirs[0])
        else:
            # Now we're in downtown
            expected_matches = {
                group: common_files
                for group in matching_groups
            }
            expected_diff = DiffResult(**expected_matches)

    validate_nest(left_dir, right_dir)
