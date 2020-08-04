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
class FilesDiff:
    changed: Set[str] = field(default_factory=set)
    missing: Set[str] = field(default_factory=set)
    new: Set[str] = field(default_factory=set)
    shared: Set[str] = field(default_factory=set)


@dataclass
class SubdirDiff:
    missing: Set[str] = field(default_factory=set)
    new: Set[str] = field(default_factory=set)
    shared: Dict[str, Tuple[Dir, Dir]] = field(default_factory=dict)


@dataclass
class DirDiff:
    files: FilesDiff = FilesDiff()
    subdirs: SubdirDiff = SubdirDiff()


# TODO: Docs
def loaded_dir(path: str) -> Dir:
    entries = listdir(path=path)

    return Dir(basename(path),
               path,
               {f for f in entries if isfile(ojoin(path, f))},
               [loaded_dir(ojoin(path, d)) for d in entries if isdir(ojoin(path, d))])


def compare_files(src_dir: Dir,
                  cmp_dir: Dir) -> FilesDiff:
    # TODO: Do something with error!!
    files_in_both = src_dir.files & cmp_dir.files
    match, mismatch, _ = cmpfiles(src_dir.fullpath,
                                  cmp_dir.fullpath,
                                  files_in_both,
                                  shallow=False)

    return FilesDiff(
        changed=set(mismatch),
        missing=(src_dir.files - files_in_both),
        new=(cmp_dir.files - files_in_both),
        shared=set(match)
    )


def compare_subdirs(src_dir: Dir,
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


# def diff_walk(src_dir: Dir,
#               cmp_dir: Dir,
#               full_paths: bool = False) -> Generator[DirDiff, None, None]:
#     left_files, right_files, common_files = compare_files(src_dir, cmp_dir)
#     left_subdirs, right_subdirs, common_subdirs = compare_subdirs(src_dir, cmp_dir)

#     yield DirDiff(
#         changed_files=left_files & right_files,
#         missing_files=left_files - right_files,
#         new_files=right_files - left_files,
#         shared_files=common_files,
#         missing_dirs=left_subdirs,
#         new_dirs=right_subdirs,
#         shared_dirs={d: (t[0].dirname, t[1].dirname) for d,t in common_subdirs.items()}
#     )

#     for left_subdir, right_subdir in common_subdirs.values():
#         yield from diff_walk(left_subdir, right_subdir)


# def full_diff_dirs(src_dir: Dir,
#                    cmp_dir: Dir,
#                    full_paths: bool = False) -> DirDiff:

#     def combine_diffs(d1: DirDiff, d2: DirDiff) -> DirDiff:
#         d1.changed_files |= d2.changed_files
#         d1.missing_files |= d2.missing_files
#         d1.new_files |= d2.new_files
#         d1.shared_files |= d2.shared_files
#         d1.missing_dirs |= d2.missing_dirs
#         d1.new_dirs |= d2.new_dirs
#         d1.shared_dirs.update(d2.shared_dirs)

#         return d1

#     return reduce(combine_diffs, diff_walk(src_dir, cmp_dir, full_paths=full_paths))
