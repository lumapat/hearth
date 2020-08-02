from __future__ import annotations

from dataclasses import dataclass, asdict
from filecmp import cmpfiles
from functools import total_ordering
from os import listdir
from os.path import basename, isdir, isfile, join as ojoin
from typing import Dict, List, Set, Tuple


@total_ordering
@dataclass(eq=False, order=False)
class Dir:
    dirname: str
    fullpath: str
    files: Set[str]
    subdirs: List[Dir]

    def __eq__(self, other):
        self.dirname.__eq__(other.dirname)

    def __lt__(self, other):
        self.dirname.__lt__(other.dirname)

    def asdict(self):
        return asdict(self)


# TODO: Docs
def loaded_dir(path: str) -> Dir:
    entries = listdir(path=path)

    return Dir(basename(path),
                path,
                {f for f in entries if isfile(ojoin(path, f))},
                [loaded_dir(ojoin(path, d)) for d in entries if isdir(ojoin(path, d))])


def compare_files(left_dir: Dir, right_dir: Dir) -> Tuple[Set[str], Set[str], Set[str]]:
    match, _, _ = cmpfiles(left_dir.fullpath,
                           right_dir.fullpath,
                           left_dir.files & right_dir.files,
                           shallow=False)

    both = set(match)
    left_only = left_dir.files - both
    right_only = right_dir.files - both

    return left_only, right_only, both


def left_dirs_only(left_dir: Dir, right_dir: Dir) -> Set[str]:
    left_subdir_set = set(d.dirname for d in left_dir.subdirs)
    right_subdir_set = set(d.dirname for d in right_dir.subdirs)
    return left_subdir_set - right_subdir_set


def right_dirs_only(left_dir: Dir, right_dir: Dir) -> Set[str]:
    left_subdir_set = set(d.dirname for d in left_dir.subdirs)
    right_subdir_set = set(d.dirname for d in right_dir.subdirs)
    return right_subdir_set - left_subdir_set


def common_dirs(left_dir: Dir, right_dir: Dir) -> Dict[str, Tuple[Dir, Dir]]:
    """ TODO: Docs

        Returns:
            A dict of common subdirectory names to a pair consisting of the left and right
            subdir in their respective positions
    """
    left_subdir_dict = {d.dirname: d for d in left_dir.subdirs}
    right_subdir_dict = {d.dirname: d for d in right_dir.subdirs}
    common_dir_names = left_subdir_dict.keys() & right_subdir_dict.keys()

    return {d: (left_subdir_dict[d], right_subdir_dict[d]) for d in common_dir_names}
