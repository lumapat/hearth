import click
import filecmp
import psutil
import pprint

pp = pprint.PrettyPrinter(indent=4)

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
    # Use psutil
    partitions = psutil.disk_partitions()
    pp.pprint(partitions)

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
def sync_cmd():
    print("To be implemented!")

def main():
    root.add_command(compare_cmd)
    root.add_command(list_cmd)
    root.add_command(sync_cmd)
    root()

if __name__ == "__main__":
    main()

