import os
from functools import partial
from subprocess import check_call
from typing import List

from build_utils import cd, build_in_tmp_directory, fetch_archive


def _get_zip_archive(url: str, digest: str, public_keys: List[str]):
    os.mkdir("build")
    with cd("build"):
        filename = fetch_archive(digest, url, public_keys)

        check_call([
            "unzip",
            "-q",
            filename,
        ])

        os.unlink(filename)


def get_zip_archive(app_name: str, url: str, digest: str, public_keys: List[str]):
    build_in_tmp_directory(
        app_name,
        digest,
        partial(_get_zip_archive, url, digest, public_keys)
    )
