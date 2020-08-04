from __future__ import annotations

from dataclasses import asdict, dataclass, field
from filecmp import cmpfiles
from functools import reduce, total_ordering
from os import listdir
from os.path import basename, isdir, isfile, join as ojoin
from typing import Dict, Generator, List, Set, Tuple


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


@dataclass
class DirDiff:
    changed_files: Set[str] = field(default_factory=set)
    missing_files: Set[str] = field(default_factory=set)
    new_files: Set[str] = field(default_factory=set)
    shared_files: Set[str] = field(default_factory=set)

    missing_dirs: Set[str] = field(default_factory=set)
    new_dirs: Set[str] = field(default_factory=set)
    shared_dirs: Dict[str, Tuple[str, str]] = field(default_factory=dict)


# TODO: Docs
def loaded_dir(path: str) -> Dir:
    entries = listdir(path=path)

    return Dir(basename(path),
               path,
               {f for f in entries if isfile(ojoin(path, f))},
               [loaded_dir(ojoin(path, d)) for d in entries if isdir(ojoin(path, d))])


def compare_files(left_dir: Dir,
                  right_dir: Dir) -> Tuple[Set[str], Set[str], Set[str]]:
    match, _, _ = cmpfiles(left_dir.fullpath,
                           right_dir.fullpath,
                           left_dir.files & right_dir.files,
                           shallow=False)

    both = set(match)
    left_only = left_dir.files - both
    right_only = right_dir.files - both

    return left_only, right_only, both


def compare_subdirs(left_dir: Dir,
                    right_dir: Dir) -> Tuple[Set[str], Set[str], Dict[str, Tuple[Dir, Dir]]]:
    """ TODO: Docs

        Returns:
            A dict of common subdirectory names to a pair consisting of the left and right
            subdir in their respective positions
    """

    left_subdirs = {d.dirname: d for d in left_dir.subdirs}
    right_subdirs = {d.dirname: d for d in right_dir.subdirs}

    common_dir_names = left_subdirs.keys() & right_subdirs.keys()

    left_only_subdirs = set(left_subdirs.keys() - right_subdirs.keys())
    right_only_subdirs = set(right_subdirs.keys() - left_subdirs.keys())
    common_subdirs = {d: (left_subdirs[d], right_subdirs[d])
                      for d in common_dir_names}

    return left_only_subdirs, right_only_subdirs, common_subdirs


def diff_walk(src_dir: Dir,
              cmp_dir: Dir,
              full_paths: bool = False) -> Generator[DirDiff, None, None]:
    left_files, right_files, common_files = compare_files(src_dir, cmp_dir)
    left_subdirs, right_subdirs, common_subdirs = compare_subdirs(src_dir, cmp_dir)

    # Ignore common subdirs as we're recursing through them
    yield DirDiff(
        changed_files=left_files & right_files,
        missing_files=left_files - right_files,
        new_files=right_files - left_files,
        shared_files=common_files,
        missing_dirs=left_subdirs,
        new_dirs=right_subdirs,
        shared_dirs={d: (t[0].dirname, t[1].dirname) for d,t in common_subdirs.items()}
    )

    for left_subdir, right_subdir in common_subdirs.values():
        yield from diff_walk(left_subdir, right_subdir)


def full_diff_dirs(src_dir: Dir,
                   cmp_dir: Dir,
                   full_paths: bool = False) -> DirDiff:
    def combine_diffs(d1: DirDiff, d2: DirDiff) -> DirDiff:
        d1.changed_files |= d2.changed_files
        d1.missing_files |= d2.missing_files
        d1.new_files |= d2.new_files
        d1.shared_files |= d2.shared_files
        d1.missing_dirs |= d2.missing_dirs
        d1.new_dirs |= d2.new_dirs
        d1.shared_dirs.update(d2.shared_dirs)

        return d1

    return reduce(combine_diffs, diff_walk(src_dir, cmp_dir, full_paths=full_paths))
