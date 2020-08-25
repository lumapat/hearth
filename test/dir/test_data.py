from dataclasses import dataclass, field
from os import fspath
from pathlib import Path
from typing import Any, Dict, Set
import os

import pytest  # type: ignore

from helpers.dir_schemas import create_dir
import hearth.dir.data as sut
import helpers.dir_schemas


def test_dir_with_only_files(tmpdir):
    # GIVEN
    temp_path = Path(tmpdir)
    expected = sut.Dir(
        temp_path.name,
        fspath(temp_path),
        {"one", "two", "three"}
    )
    create_dir(temp_path, expected)

    # WHEN
    actual = sut.loaded_dir(temp_path)

    # THEN
    assert expected == actual


def test_dir_with_files_and_subdir(tmpdir):
    # GIVEN
    temp_path = Path(tmpdir)
    expected = sut.Dir(
        temp_path.name,
        fspath(temp_path),
        {"one", "two", "three"}
    )

    subdir_name = "sublevel1"
    expected.subdirs = {
        subdir_name: sut.Dir(
            subdir_name,
            fspath(temp_path/subdir_name),
            {"file1.txt", "file2.tsk", "file3.js"},
        )
    }

    create_dir(temp_path, expected)

    # WHEN
    actual = sut.loaded_dir(temp_path)

    # THEN
    assert expected == actual


def test_dir_with_multiple_subdir_levels(tmpdir):
    # GIVEN
    temp_path = Path(tmpdir)
    expected = helpers.dir_schemas.multiple_subdir_levels(temp_path)
    create_dir(temp_path, expected)

    # WHEN
    actual = sut.loaded_dir(temp_path)

    # THEN
    assert expected == actual
