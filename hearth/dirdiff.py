from __future__ import annotations

from copy import copy
from dataclasses import asdict, dataclass, field
from filecmp import cmpfiles
from functools import reduce, total_ordering
from os import listdir
from os.path import basename, isdir, isfile, join as ojoin
from typing import Dict, Generator, List, Set, Tuple
import operator


@total_ordering
@dataclass(eq=False, order=False)
class Dir:
    dirname: str
    fullpath: str
    files: Set[str]
    subdirs: List[Dir]

    def __eq__(self, other):
        return self.dirname.__eq__(other.dirname)

    def __lt__(self, other):
        return self.dirname.__lt__(other.dirname)

    def asdict(self):
        return asdict(self)


@dataclass
class FilesDiff:
    changed: Set[str] = field(default_factory=set)
    missing: Set[str] = field(default_factory=set)
    new: Set[str] = field(default_factory=set)
    shared: Set[str] = field(default_factory=set)

    def __or__(self, other):
        self.changed |= other.changed
        self.missing |= other.missing
        self.new |= other.new
        self.shared |= other.shared

        return self

    def __bool__(self):
        return any([
            self.changed,
            self.missing,
            self.new,
            self.shared
        ])


@dataclass
class SubdirDiff:
    missing: Set[str] = field(default_factory=set)
    new: Set[str] = field(default_factory=set)
    shared: Dict[str, Tuple[Dir, Dir]] = field(default_factory=dict)

    def __or__(self, other):
        self.missing |= other.missing
        self.new |= other.new
        self.shared.update(other.shared)

        return self

    def __bool__(self):
        return any([
            self.missing,
            self.new,
            self.shared
        ])


@dataclass
class DirDiff:
    files: FilesDiff = FilesDiff()
    subdirs: SubdirDiff = SubdirDiff()

    def __or__(self, other):
        self.files |= other.files
        self.subdirs |= other.subdirs

        return self

    def __bool__(self):
        return self.files or self.subdirs


# TODO: Docs
def loaded_dir(path: str) -> Dir:
    entries = listdir(path=path)

    return Dir(basename(path),
               path,
               {f for f in entries if isfile(ojoin(path, f))},
               [loaded_dir(ojoin(path, d)) for d in entries if isdir(ojoin(path, d))])


def _compare_files(src_dir: Dir,
                   cmp_dir: Dir) -> FilesDiff:
    # TODO: Do something with error!!
    files_in_both = src_dir.files & cmp_dir.files
    matches, mismatches, _ = cmpfiles(src_dir.fullpath,
                                      cmp_dir.fullpath,
                                      files_in_both,
                                      shallow=False)

    return FilesDiff(
        changed=set(mismatches),
        missing=(src_dir.files - files_in_both),
        new=(cmp_dir.files - files_in_both),
        shared=set(matches)
    )


def _compare_subdirs(src_dir: Dir,
                     cmp_dir: Dir) -> SubdirDiff:
    """ TODO: Docs """

    src_subdirs = {d.dirname: d for d in src_dir.subdirs}
    cmp_subdirs = {d.dirname: d for d in cmp_dir.subdirs}

    common_dir_names = src_subdirs.keys() & cmp_subdirs.keys()

    src_only_subdirs = set(src_subdirs.keys() - cmp_subdirs.keys())
    cmp_only_subdirs = set(cmp_subdirs.keys() - src_subdirs.keys())
    common_subdirs = {d: (src_subdirs[d], cmp_subdirs[d])
                      for d in common_dir_names}

    return SubdirDiff(
        missing=src_only_subdirs,
        new=cmp_only_subdirs,
        shared=common_subdirs
    )


def compare_dirs(src_dir: Dir,
                 cmp_dir: Dir) -> DirDiff:
    return DirDiff(
        files=_compare_files(src_dir, cmp_dir),
        subdirs=_compare_subdirs(src_dir, cmp_dir)
    )


def _diff_walk(src_dir: Dir,
               cmp_dir: Dir,
               full_paths: bool = False) -> Generator[DirDiff, None, None]:
    dir_diff = compare_dirs(src_dir, cmp_dir)
    subdirs = copy(dir_diff.subdirs.shared)

    yield dir_diff

    for left_subdir, right_subdir in subdirs.values():
        yield from _diff_walk(left_subdir, right_subdir)


def full_diff_dirs(src_dir: Dir,
                   cmp_dir: Dir,
                   full_paths: bool = False) -> DirDiff:

    return reduce(operator.or_,
                  _diff_walk(src_dir,
                             cmp_dir,
                             full_paths=full_paths))
