from dataclasses import dataclass, field
from typing import Any, Dict, Set
from pathlib import Path
import datetime as dt

import pytest # type: ignore

import hearth.dirsync as sut


def test_save_and_get_dirsync_toml(tmpdir):
    now = dt.datetime.now()
    sample_path = str(Path.home())
    sample_infos = {f"sample{i}": sut.SyncInfo(
        f"sample{i}",
        f"Sample {i} description. Beep boop",
        "s1",
        {"s1": sample_path, "s2": sample_path}
    ) for i in range(1,4)}
    sample_file = Path(str(tmpdir)) / "sample.toml"

    expected_central = sut.SyncCentral(sample_file, now, now, sample_infos)

    sut.save_sync_central(expected_central)
    actual_central = sut.get_sync_central(sample_file)

    assert expected_central == actual_central
