from __future__ import annotations

from copy import copy
from dataclasses import asdict, dataclass, field
from filecmp import cmpfiles
from functools import reduce, total_ordering
from os import listdir
from os.path import basename, isdir, isfile, join as ojoin
from pathlib import Path
from typing import (
    Dict,
    Generator,
    Iterable,
    List,
    Set,
    Tuple
)
import operator


@total_ordering
@dataclass(eq=False, order=False)
class Dir:
    dirname: str
    fullpath: str
    files: Set[str] = field(default_factory=set)
    subdirs: Dict[str, Dir] = field(default_factory=dict)

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
    shared: Set[str] = field(default_factory=set)

    def __or__(self, other):
        self.missing |= other.missing
        self.new |= other.new
        self.shared |= other.shared

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

    subdirs = {d: loaded_dir(ojoin(path, d)) for d in entries if isdir(ojoin(path, d))}
    files =  {f for f in entries if isfile(ojoin(path, f))}

    return Dir(basename(path), path, files=files, subdirs=subdirs)


def _prepend_path(paths: Iterable[str],
                  path: str) -> Set[str]:
    if path:
        return set(ojoin(path, p) for p in paths)
    else:
        return set(paths)


def _compare_files(src_dir: Dir,
                   cmp_dir: Dir,
                   prefix_path: str = "") -> FilesDiff:
    # TODO: Do something with error!!
    files_in_both = src_dir.files & cmp_dir.files
    matches, mismatches, _ = cmpfiles(src_dir.fullpath,
                                      cmp_dir.fullpath,
                                      files_in_both,
                                      shallow=False)

    return FilesDiff(
        changed=_prepend_path(mismatches, prefix_path),
        missing=_prepend_path(src_dir.files - files_in_both, prefix_path),
        new=_prepend_path(cmp_dir.files - files_in_both, prefix_path),
        shared=_prepend_path(matches, prefix_path)
    )


def _compare_subdirs(src_dir: Dir,
                     cmp_dir: Dir,
                     prefix_path: str = "") -> SubdirDiff:
    """ TODO: Docs """

    src_subdirs = set(src_dir.subdirs.keys())
    cmp_subdirs = set(cmp_dir.subdirs.keys())

    return SubdirDiff(
        missing=_prepend_path(src_subdirs - cmp_subdirs, prefix_path),
        new=_prepend_path(cmp_subdirs - src_subdirs, prefix_path),
        shared=_prepend_path(src_subdirs & cmp_subdirs, prefix_path)
    )


def compare_dirs(src_dir: Dir,
                 cmp_dir: Dir,
                 prefix_path: str = "") -> DirDiff:
    return DirDiff(
        files=_compare_files(src_dir, cmp_dir, prefix_path=prefix_path),
        subdirs=_compare_subdirs(src_dir, cmp_dir, prefix_path=prefix_path)
    )


def _diff_walk(src_dir: Dir,
               cmp_dir: Dir,
               relative_path: str = "",
               full_paths: bool = False) -> Generator[DirDiff, None, None]:
    dir_diff = compare_dirs(src_dir, cmp_dir, prefix_path=relative_path)
    subdirs = copy(dir_diff.subdirs.shared)

    yield dir_diff

    for subdir in subdirs:
        base_subdir = basename(subdir)
        yield from _diff_walk(src_dir.subdirs[base_subdir],
                              cmp_dir.subdirs[base_subdir],
                              relative_path=subdir,
                              full_paths=full_paths)


def full_diff_dirs(src_dir: Dir,
                   cmp_dir: Dir,
                   full_paths: bool = False) -> DirDiff:

    return reduce(operator.or_,
                  _diff_walk(src_dir,
                             cmp_dir,
                             full_paths=full_paths))
