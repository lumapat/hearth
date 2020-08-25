from __future__ import annotations

from hearth.dir.data import Dir

from copy import copy
from dataclasses import dataclass, field
from filecmp import cmpfiles
from os import listdir
from os.path import basename, isdir, isfile, join as ojoin
from pathlib import Path
from queue import Queue
from typing import (
    Dict,
    Generator,
    Iterable,
    List,
    Set,
)
import logging


logger = logging.getLogger(__name__)


@dataclass
class FilesDiff:
    changed: Set[str] = field(default_factory=set)
    missing: Set[str] = field(default_factory=set)
    new: Set[str] = field(default_factory=set)
    shared: Set[str] = field(default_factory=set)

    def __or__(self, other) -> FilesDiff:
        self.changed |= other.changed
        self.missing |= other.missing
        self.new |= other.new
        self.shared |= other.shared

        return self

    def __bool__(self) -> bool:
        return any([
            self.changed,
            self.missing,
            self.new
        ])


@dataclass
class SubdirDiff:
    missing: Set[str] = field(default_factory=set)
    new: Set[str] = field(default_factory=set)
    shared: Set[str] = field(default_factory=set)

    def __or__(self, other) -> SubdirDiff:
        self.missing |= other.missing
        self.new |= other.new
        self.shared |= other.shared

        return self

    def __bool__(self) -> bool:
        return any([
            self.missing,
            self.new
        ])


@dataclass
class DirDiff:
    files: FilesDiff = FilesDiff()
    subdirs: SubdirDiff = SubdirDiff()

    def __or__(self, other) -> DirDiff:
        self.files |= other.files
        self.subdirs |= other.subdirs

        return self

    def __bool__(self) -> bool:
        return any([self.files, self.subdirs])


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


def _compare_dirs(src_dir: Dir,
                  cmp_dir: Dir,
                  prefix_path: str = "") -> DirDiff:
    return DirDiff(
        files=_compare_files(src_dir, cmp_dir, prefix_path=prefix_path),
        subdirs=_compare_subdirs(src_dir, cmp_dir, prefix_path=prefix_path)
    )


def _full_diff_helper(src_dir: Dir,
                      cmp_dir: Dir,
                      relative_path: str = "",
                      full_paths: bool = False) -> DirDiff:
    dir_diff = _compare_dirs(src_dir, cmp_dir, prefix_path=relative_path)

    subdirs = copy(dir_diff.subdirs.shared)
    dir_diff.subdirs.shared.clear()

    for subdir in subdirs:
        base_subdir = basename(subdir)
        subdir_diff = _full_diff_helper(src_dir.subdirs[base_subdir],
                                        cmp_dir.subdirs[base_subdir],
                                        relative_path=subdir,
                                        full_paths=full_paths)

        if subdir_diff:
            dir_diff |= subdir_diff
        else:
            dir_diff.subdirs.shared.add(subdir)

    return dir_diff


def full_diff_dirs(src_dir: Dir,
                   cmp_dir: Dir,
                   full_paths: bool = False) -> DirDiff:

    return _full_diff_helper(src_dir,
                             cmp_dir,
                             full_paths=full_paths)
