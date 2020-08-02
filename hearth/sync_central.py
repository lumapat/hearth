from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict
from pathlib import Path
import toml


@dataclass
class Device:
    name: str
    mountpoint: str


@dataclass
class SyncInfo:
    name: str
    description: str
    primary_source: str
    sources: Dict[str, str]


@dataclass
class SyncCentral:
    data_file_path: str
    devices: Dict[str, Device]
    last_modified: datetime
    last_synced: datetime
    sync_infos: Dict[str, SyncInfo]


class SyncError(Exception):
    pass


def get_sync_central(path: Path) -> SyncCentral:
    if not path.is_file():
        raise SyncError(f"'{path}' doesn't exist")

    with path.open() as f:
        central_dict = toml.load(f)

        sync_infos = {
            name: SyncInfo(**info)
            for name, info in central_dict["sync_infos"].items()
        }

        devices = {
            name: Device(**info)
            for name, info in central_dict["devices"].items()
        }

        last_modified = central_dict["last_modified"]
        last_synced = central_dict["last_synced"]

        return SyncCentral(path, devices, last_modified, last_synced, sync_infos)


def save_sync_central(central: SyncCentral,
                      create_if_exists: bool = False) -> None:
    central_dict = asdict(central)

    # Don't need to save this
    central_dict["data_file_path"] = None
    path = Path(central.data_file_path)

    if not path.exists():
        if create_if_exists:
            # TODO: Log here
            path.touch()
        else:
            raise SyncError(f"'{path}' doesn't exist")

    with path.open(mode="w") as f:
        toml.dump(central_dict, f)
