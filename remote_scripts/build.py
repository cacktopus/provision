import os
import subprocess
import sys
from functools import partial
from subprocess import check_call

from build_utils import cd, build_in_tmp_directory
from setup_user import ensure_dir
from util import log, find_program, timeit


def _build(name: str, repo: str, commit: str):
    # This is responsible for creating a build/ directory and building in it

    exe = find_program("git", "/usr/bin")

    def git(cmd):
        log(f"{exe} {cmd}")
        return check_call([exe] + cmd.split())

    git_home = os.path.expanduser("~/git")
    ensure_dir(git_home, 0o700)

    dst = repo.split("/")[-1]

    with cd(git_home):
        local_repo = os.path.abspath(dst)

        if not os.path.exists(dst):
            git(f"init -q --bare {dst}")
        with cd(dst):
            git("config --local uploadpack.allowreachablesha1inwant true")
            rc, existing_repo = subprocess.getstatusoutput(f"{exe} remote get-url origin")
            if rc != 0:
                git(f"remote add origin {repo}")
            elif existing_repo.strip() != repo:
                git(f"remote set-url origin {repo}")

            with timeit("remote fetch"):
                git("fetch")

    cmd = f"init -q build"
    git(cmd)

    with cd("build"):
        git(f"remote add origin {local_repo}")
        with timeit("local fetch"):
            git(f"fetch -q origin {commit} --depth 1")
        git(f"reset -q --hard {commit}")
        with timeit("build"):
            subprocess.check_call(f"./services/{name}/build.sh", stdout=sys.stderr)


def build(name, repo, commit):
    build_in_tmp_directory(
        name,
        commit,
        partial(_build, name, repo, commit)
    )
