from datetime import datetime
from pathlib import Path
from os import curdir, path

import click
import filecmp
import logging
import psutil  # type: ignore
import pprint
import shutil
import sys

from hearth import sync_central

pp: pprint.PrettyPrinter = pprint.PrettyPrinter(indent=4)
DEFAULT_SAVE_FILENAME = ".hearth-central.toml"
DEFAULT_SAVE_PATH: Path = Path.home() / DEFAULT_SAVE_FILENAME

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format="%(asctime)s - %(message)s")


@click.group()
def root():
    pass


@click.command(
    name="compare",
    short_help="Compare the contents of two or more directories"
)
@click.argument("src")
@click.argument("target")
def compare_cmd(src, target):
    res = filecmp.dircmp(src, target)
    res.report_full_closure()


@click.command(
    name="init",
    short_help="Initialize hearth on the current system"
)
def init_cmd():
    devices = {
        p.device: sync_central.Device(p.device, p.mountpoint)
        for p in psutil.disk_partitions()
    }

    now = datetime.now()
    central = sync_central.SyncCentral(
        str(DEFAULT_SAVE_PATH),
        devices,
        now,
        now,
        {}
    )

    sync_central.save_sync_central(central, create_if_exists=True)
    logger.info(f"Initialized hearth into '{DEFAULT_SAVE_PATH}'")


# Roadmap for list:
# Create a centralized YAML to store this (for now)
#	- Not sure if we need a more persistent store but this should be enough
# If the YAML already exists, use it
# YAML should have the following information
#	- List of hearths to keep burning!
#		- Root folder location
#		- Device name
#		- Type of storage (e.g. USB, SSD, HDD)
#
# YAML will eventually have more information, and the information may
# need to be de-centralized for better robustness. But good to defer this.

# For now, just list all the storage devices on the system!
@click.command(
    name="list",
    short_help="List the storage devices and save points in a system"
)
def list_cmd():
    try:
        central = sync_central.get_sync_central(DEFAULT_SAVE_PATH)

        # TODO: Print better than this
        pp.pprint(central)
    except sync_central.SyncError:
        logger.info("Current system is uninitialized."
                    " Could not retrieve any save points or system details."
                    " Please run 'hearth init' to initialize first.")
        return


# TODO: Implement a sync
#
# Might need to share the code from Compare
# but this command will need to sync files based on a
# list of strategies
#	- TrueMasterCopy (Highest priority ID)
#		- Delete data not found in MasterCopy
#		- Add only new data found only in MasterCopy
#	- NewFilesOnly
#		- Add only new data found in any copy across all copies
#  - AddByMasterCopy
#		- Add only new data found only in MasterCopy
#		- Keep data existing in other copies
#  - TrimByMasterCopy
#		- Delete data not found in MasterCopy
#		- Do not add other data
@click.command(
    name="sync",
    short_help="Sync the contents of two or more storage devices"
)
@click.argument("master")
@click.argument("backup")
@click.option("--no-commit", is_flag=True, help="Do not commit sync")
def sync_cmd(master, backup, no_commit):

    def flatten_left_only(dc, prefix):
        lefts = [path.join(prefix, l) for l in dc.left_only]

        if dc.subdirs:
            return lefts + [e for d, l in dc.subdirs.items() for e in flatten_left_only(l, d)]
        else:
            return lefts

    res = flatten_left_only(filecmp.dircmp(master, backup), "")

    if no_commit:
        print(
            f"Syncing the following data from {master} to {backup}: {pp.pformat(res)}")
    else:
        print(f"Syncing {master} contents to {backup}...")
        for e in res:
            master_copy = path.join(master, e)
            backup_copy = path.join(backup, e)

            if path.isfile(master_copy):
                shutil.copy(master_copy, backup_copy)
                print(f"File {master_copy} >>>> {backup_copy}")
            else:
                shutil.copytree(master_copy, backup_copy)
                print(f"Directory {master_copy} >>>> {backup_copy}")


def main():
    root.add_command(compare_cmd)
    root.add_command(init_cmd)
    root.add_command(list_cmd)
    root.add_command(sync_cmd)
    root()


if __name__ == "__main__":
    main()
