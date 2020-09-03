from __future__ import annotations

import logging
from dataclasses import dataclass, field
from functools import total_ordering
from os import PathLike, listdir
from pathlib import Path
from queue import Queue
from typing import Callable, Dict, Set

logger = logging.getLogger(__name__)

@total_ordering
@dataclass(eq=False, order=False)
class Dir:
    dirname: str
    fullpath: PathLike
    files: Set[str] = field(default_factory=set)
    subdirs: Dict[str, Dir] = field(default_factory=dict)

    def __eq__(self, other):
        return self.dirname.__eq__(other.dirname)

    def __lt__(self, other):
        return self.dirname.__lt__(other.dirname)


def loaded_dir(path: PathLike) -> Dir:
    """ Load directory in the specified path into a Dir object """
    entries = listdir(path=path)
    p = Path(path)

    subdirs = {d: loaded_dir(p/d) for d in entries if (p/d).is_dir()}
    files =  {f for f in entries if (p/f).is_file()}

    return Dir(p.name, path, files=files, subdirs=subdirs)


# TODO: Docs
def dir_walk(dir_: Dir,
             func: Callable[[Dir], None]) -> None:
    remaining_dirs: Queue = Queue()
    remaining_dirs.put(dir_)

    while not remaining_dirs.empty():
        curr_dir = remaining_dirs.get()

        func(curr_dir)

        for d in curr_dir.subdirs.values():
            remaining_dirs.put(d)
