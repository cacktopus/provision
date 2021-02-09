import glob
import inspect
import os
from contextlib import contextmanager
from functools import partial
from subprocess import check_call

from build_utils import build_in_tmp_directory, fetch_archive
from util import log


@contextmanager
def mutate():
    stack = inspect.stack()[1:]
    for row in stack:
        if row.filename == __file__:
            log("mutate in", row.function, row.lineno)
            break
    else:
        raise RuntimeError("Unable to determine line number")

    yield


def _get_tar_archive(url: str, digest: str, flags: str):
    filename = fetch_archive(digest, url)

    check_call([
        "tar",
        flags, filename
    ])

    os.unlink(filename)

    files = glob.glob("./*")
    log(files)

    assert len(files) == 1, "Expecting the tar archive to only contain one entry"

    f = files[0]
    if os.path.isdir(f):
        os.rename(f, "build")
    elif os.path.isfile(f):
        os.mkdir("build")
        os.rename(f, f"build/{f}")
    else:
        assert False, "unexpected file type"


def get_tar_archive(app_name: str, url: str, digest: str):
    build_in_tmp_directory(
        app_name,
        digest,
        partial(_get_tar_archive, url, digest, "-xf")
    )


def get_tar_bz_archive(app_name: str, url: str, digest: str):
    build_in_tmp_directory(
        app_name,
        digest,
        partial(_get_tar_archive, url, digest, "-xjf")
    )
