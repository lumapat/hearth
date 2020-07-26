from typing import Any, Dict
from pathlib import Path
import os
import pytest

from hearth.dirdiff import Dir


def create_dir(path: str, dir_dict: Dict[str, Any]) -> None:
    """ Creates a directory in the specified path

    :param path: Path to create directory in
    :param dir_dict: Specification of contents to create in directory
    """
    for f in dir_dict["files"]:
        Path(os.path.join(path, f)).touch()

    for contents in dir_dict["subdirs"]:
        subdir_path = os.path.join(path, contents["dirname"])
        Path(subdir_path).mkdir()

        create_dir(subdir_path, contents)


@pytest.mark.dir_ctor
def test_dir_with_only_files(tmpdir):
    # GIVEN
    temp_path = str(tmpdir)
    expected = {
        "dirname": os.path.basename(temp_path),
        "files": {"one", "two", "three"},
        "subdirs": []
    }
    create_dir(temp_path, expected)

    # WHEN
    actual = Dir(temp_path)

    # THEN
    assert expected == actual.asdict()


@pytest.mark.dir_ctor
def test_dir_with_files_and_subdir(tmpdir):
    # GIVEN
    temp_path = str(tmpdir)
    expected = {
        "dirname": os.path.basename(temp_path),
        "files": {"one", "two", "three"},
        "subdirs": [{
            "dirname": "sublevel1",
            "files": {"file1.txt", "file2.tsk", "file3.js"},
            "subdirs": []
        }]
    }
    create_dir(temp_path, expected)

    # WHEN
    actual = Dir(temp_path)

    # THEN
    assert expected == actual.asdict()


@pytest.mark.dir_ctor
def test_dir_with_multiple_subdir_levels(tmpdir):
    # GIVEN
    temp_path = str(tmpdir)
    expected = {
        "dirname": os.path.basename(temp_path),
        "files": {"one"},
        "subdirs": [{
            "dirname": "sublevel1",
            "files": {"file1.txt", "file2.tsk"},
            "subdirs": [{
                "dirname": "sublevel2",
                "files": {"ugh.js", "ayy.css", "nope.html"},
                "subdirs": [{
                    "dirname": "Secret Pictures",
                    "files": {"SECRET.png"},
                    "subdirs": []
                }]
            },
            {
                "dirname": "Pictures",
                "files": {"img1.jpg", "img2.jpg", "vid1.mp4"},
                "subdirs": []
            }]
        }]
    }
    create_dir(temp_path, expected)

    # WHEN
    actual = Dir(temp_path)

    # THEN
    assert expected == actual.asdict()
