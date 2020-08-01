from __future__ import annotations

from dataclasses import dataclass, asdict
from filecmp import cmpfiles
from functools import total_ordering
from os import listdir
from os.path import basename, isdir, isfile, join as ojoin
from typing import List, Set, Tuple


@total_ordering
@dataclass(init=False, eq=False, order=False)
class Dir:
    dirname: str
    fullpath: str
    files: Set[str]
    subdirs: List[Dir]

    def __init__(self, path):
        self.dirname = basename(path)
        self.fullpath = path

        entries = listdir(path=path)
        self.files = {f for f in entries if isfile(ojoin(path, f))}
        self.subdirs = [Dir(ojoin(path, d)) for d in entries if isdir(ojoin(path, d))]

    def __eq__(self, other):
        self.dirname.__eq__(other.dirname)

    def __lt__(self, other):
        self.dirname.__lt__(other.dirname)

    def asdict(self):
        return asdict(self)


def left_only(left_dir: Dir, right_dir: Dir) -> Set[str]:
    return left_dir.files - both(left_dir, right_dir)


def right_only(left_dir: Dir, right_dir: Dir) -> Set[str]:
    return right_dir.files - both(left_dir, right_dir)


def both(left_dir: Dir, right_dir: Dir) -> Set[str]:
    match, _, _ = cmpfiles(left_dir.files,
                           right_dir.files,
                           left_dir.files & right_dir.files,
                           shallow=False)
    return set(match)


def left_dirs_only(left_dir: Dir, right_dir: Dir) -> Set[str]:
    return left_dir.subdirs - right_dir.subdirs


def right_dirs_only(left_dir: Dir, right_dir: Dir) -> Set[str]:
    return right_dir.subdirs - left_dir.subdirs


def common_dirs(left_dir: Dir, right_dir: Dir) -> List[Dir]:
    return left_dir.subdirs & right_dir.subdirs
