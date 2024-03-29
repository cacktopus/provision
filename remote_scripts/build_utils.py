import getpass
import hashlib
import os
import tempfile
from contextlib import contextmanager
from subprocess import check_call
from typing import Iterator, Any, Callable, List

from util import log


@contextmanager
def cd(path: str) -> Iterator[Any]:
    cur = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(cur)


def build_in_tmp_directory(app_name: str, digest: str, build_callback: Callable[[], None]) -> None:
    # TODO: have callbacks build into a build/ directory to avoid awkwardness
    os.umask(0o027)

    user = getpass.getuser()
    builds = os.path.join(os.path.expanduser(f"~{user}/builds"), app_name)

    if not os.path.isdir(builds):
        os.makedirs(builds)

    target = os.path.join(builds, digest)
    prod_link = os.path.join(builds, "prod")

    log("target", target)
    log("prod", prod_link)

    if os.path.isdir(target):
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        log(tmpdir)
        with cd(tmpdir):
            build_callback()

            log("rename", digest, target)
            os.rename("build", target)

            # atomic prod link swap
            os.symlink(digest, "prod", target_is_directory=True)
            os.rename("prod", prod_link)


def hashfile(filename: str, hashfunc: Callable[[], Any] = hashlib.sha256) -> str:
    d = hashfunc()
    with open(filename, "rb") as fp:
        while True:
            buf = fp.read(64 * 1024)
            if len(buf) == 0:
                break
            d.update(buf)
    result: str = d.hexdigest()
    return result


def fetch_archive(
        digest: str,
        url: str,
        allowed_digests: List[str],
        public_keys: List[str]
) -> str:
    filename = url.split("/")[-1]

    check_call(["curl", "-L", "-O", url])
    assert os.path.isfile(filename)

    hash = hashfile(filename)
    log("computed hash:", hash)
    assert hash == digest, f"{hash} vs. {digest}"

    if hash in allowed_digests:
        pass

    else:
        check_call(["curl", "-L", "-O", url + ".minisig"])
        assert os.path.isfile(filename + ".minisig")

        pubkey_args = []
        for p in public_keys:
            pubkey_args.append("--public-key")
            pubkey_args.append(p)

        verify_cmd = ["/home/build/builds/minisign-verify/prod/minisign-verify"] + pubkey_args + [filename]
        log(" ".join(verify_cmd))
        check_call(verify_cmd)

        os.unlink(filename + ".minisig")

    return filename
