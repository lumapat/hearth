from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict
from pathlib import Path
import toml


@dataclass
class SyncInfo:
    name: str
    description: str
    primary_source: str
    sources: Dict[str, str]


@dataclass
class SyncCentral:
    data_file_path: str
    last_modified: datetime
    last_synced: datetime
    sync_infos: Dict[str, SyncInfo]


# TODO: Use different exceptions
def get_sync_central(path: Path) -> SyncCentral:
    if not path.is_file():
        raise Exception("")

    with path.open() as f:
        central_dict = toml.load(f)

        sync_infos = {
            name: SyncInfo(
                name,
                info["description"],
                info["primary_source"],
                {src_name: src_path for src_name, src_path in info["sources"].items()}
            ) for name, info in central_dict["sync_infos"].items()
        }

        last_modified = central_dict["last_modified"]
        last_synced = central_dict["last_synced"]

        return SyncCentral(path, last_modified, last_synced, sync_infos)


def save_sync_central(central: SyncCentral) -> None:
    central_dict = asdict(central)

    # Don't need to save this
    central_dict["data_file_path"] = None
    path = Path(central.data_file_path)

    # TODO: Make this an option so we can error/prompt appropriately on it
    if not path.exists():
        path.touch()

    with path.open(mode="w") as f:
        toml.dump(central_dict, f)
