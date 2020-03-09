import os
import sys
import time
from contextlib import contextmanager
from typing import Any, Optional, Generator, Iterator


def log(*args: Any) -> None:
    print(*args, file=sys.stderr, flush=True)


def find_program(name: str, *paths: str) -> Optional[str]:
    for path in paths:
        fullpath = os.path.join(path, name)
        if os.path.isfile(fullpath):
            return fullpath
    return None


@contextmanager
def timeit(description: str) -> Iterator[Any]:
    t0 = time.time()
    yield
    t1 = time.time()
    dt = t1 - t0
    log(f'timing: "{description}" took {dt:.2f}s')


@contextmanager
def umask(mask: int) -> Iterator[Any]:
    oldmask = os.umask(mask)
    yield
    os.umask(oldmask)

