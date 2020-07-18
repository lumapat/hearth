from dataclasses import dataclass, asdict
from filecmp import cmpfiles
from functools import total_ordering
from os import listdir
from os.path import isdir, isfile, join as ojoin
from typing import Set, Tuple


@total_ordering
@dataclass(init=False, eq=False, order=False)
class Dir:
    dirname: str
    files: Set[str]
    subdirs: Set[Dir]

    def __init__(self, dirname):
        self.dirname = dirname

        entries= listdir(path=dirname)
        self.files = {f for f in entries if isfile(f)}
        self.subdirs = {Dir(d)for d in entries if isdir(d)}

    def __eq__(self, other):
        self.dirname.__eq__(other.dirname)

    def __lt__(self, other):
        self.dirname.__lt__(other.dirname)

    def asdict(self):
        return asdict(self)


def left_only(left_dir: Dir, right_dir: Dir) -> Set[str]:
    return left_dir.files - both()


def right_only(left_dir: Dir, right_dir: Dir) -> Set[str]:
    return right_dir.files - both()


def both(left_dir: Dir, right_dir: Dir) -> Set[str]:
    match, mismatch, errors = cmpfiles(left_dir.files,
                                       right_dir.files,
                                       left_dir.files & right_dir.files.
                                       shallow=False)
    return set(match)


def left_dirs_only(left_dir: Dir, right_dir: Dir) -> Set[str]:
    return left_dir.subdirs - right_dir.subdirs


def right_dirs_only(left_dir: Dir, right_dir: Dir) -> Set[str]:
    return right_dir.subdirs - left_dir.subdirs


def common_dirs(left_dir: Dir, right_dir: Dir) -> List[DirCmp]:
    common_dirs = left_dir.subdirs & right_dir.subdirs
    return [
        DirCmp(ojoin(left_dir.dirname, d),
               ojoin(right_dir.dirname, d))
        for d in common_dirs
    ]