import os
import subprocess
from functools import partial
from subprocess import check_call

from build_utils import cd, build_in_tmp_directory


def _build_node(name: str, repo: str, commit: str):
    # This is responsible for creating a build/ directory and building in it

    cmd = "git clone {repo} --no-checkout build".format(**locals()).split()
    check_call(cmd)

    with cd("build"):
        cmd = "git checkout {commit}".format(**locals()).split()
        check_call(cmd)

        with cd("boss-ui"):  # TODO!!
            mybin = os.path.expanduser("~/bin")
            env = dict(os.environ, PATH=os.environ['PATH'] + ":" + mybin)
            check_call(["npm", "install"], env=env)
            check_call(["npm", "run", "build"], env=env)

            check_call(["rm", "-rf", "node_modules"])

            if os.path.isfile("post_build.sh"):
                subprocess.check_call(["./post_build.sh"])


def build_node(name, repo, commit):
    build_in_tmp_directory(
        name,
        commit,
        partial(_build_node, name, repo, commit)
    )
