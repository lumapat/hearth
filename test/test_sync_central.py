from dataclasses import dataclass, field
from typing import Any, Dict, Set
from pathlib import Path
import datetime as dt

import pytest # type: ignore

import hearth.sync_central as sut


def generate_sample_sync_central(path: Path):
    now = dt.datetime.now()
    sample_path = str(Path.home())
    sample_infos = {f"sample{i}": sut.SyncInfo(
        f"sample{i}",
        f"Sample {i} description. Beep boop",
        "s1",
        {"s1": sample_path, "s2": sample_path}
    ) for i in range(1,4)}
    devices = {f"device{i}": sut.Device(
        f"device{i}",
        f"/mount/somewhere/device{i}"
    ) for i in range(1,3)}

    return sut.SyncCentral(str(path), devices, now, now, sample_infos)


def test_get_dirsync_toml_that_doesnt_exist(tmpdir):
    # Didn't do any work to set up the file
    sample_path = Path(str(tmpdir)) / "sample.toml"

    try:
        sut.get_sync_central(sample_path)
        assert False
    except sut.SyncError as e:
        assert str(e)


def test_save_nonexistent_toml(tmpdir):
    # Didn't do any work to set up the file
    sample_path = Path(str(tmpdir)) / "sample.toml"
    sample_sync_central = generate_sample_sync_central(sample_path)

    try:
        sut.save_sync_central(sample_sync_central, create_if_exists=False)
        assert False
    except sut.SyncError as e:
        assert str(e)

    sut.save_sync_central(sample_sync_central, create_if_exists=True)
    assert sample_path.exists()


def test_save_and_get_dirsync_toml(tmpdir):
    sample_file = Path(str(tmpdir)) / "sample.toml"
    expected_central = generate_sample_sync_central(sample_file)

    sut.save_sync_central(expected_central, create_if_exists=True)
    actual_central = sut.get_sync_central(sample_file)

    assert expected_central == actual_central
