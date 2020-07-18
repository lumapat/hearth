from typing import Any, Dict
import pytest

from hearth.dircmp import Dir


def create_dir(path: str, dir_dict: Dict[Any]):
    pass None


def test_dir_with_only_files(temp_path):
    # GIVEN
    expected = {
        "dirname": temp_path,
        "files": {"one", "two", "three"},
        "subdirs": {}
    }
    create_dir(temp_path, expected)

    # WHEN
    actual = Dir(temp_path)

    # THEN
    assert expected == actual.asdict()


def test_dir_with_files_and_subdir(temp_path):
    # GIVEN
    expected = {
        "dirname": temp_path,
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


def test_dir_with_multiple_subdir_levels(temp_path):
    # GIVEN
    expected = {
        "dirname": temp_path,
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
