from __future__ import annotations

from dataclasses import dataclass, field
from functools import total_ordering
from queue import Queue
from typing import (
    Dict,
    Callable,
    Set,
)
import logging


logger = logging.getLogger(__name__)

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


def dir_walk(dir_: Dir,
             func: Callable[[Dir], None]) -> None:
    remaining_dirs = Queue()
    remaining_dirs.put(dir_)

    while not remaining_dirs.empty():
        curr_dir = remaining_dirs.get()

        func(curr_dir)

        for d in curr_dir.subdirs.values():
            remaining_dirs.put(d)

