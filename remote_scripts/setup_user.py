import os
import platform
import subprocess
import tempfile
from grp import getgrnam
from pwd import getpwnam
from typing import List, Tuple, Dict, Optional

import build_utils
import util
from build_utils import cd
from util import log, find_program


def run(cmd: List[str]) -> Tuple[int, str, str]:
    log(" ".join(cmd))
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        rc = p.wait()
        stdout = p.stdout.read().decode()
        stderr = p.stderr.read().decode()
        return rc, stdout, stderr


def check(cmd: List[str], env: Optional[Dict[str, str]] = None) -> str:
    log(" ".join(cmd))
    try:
        result = subprocess.check_output(cmd, env=env).decode().rstrip()
        return result
    except subprocess.CalledProcessError as e:
        log(f"error: {e.output}")
        raise


def has_user(username: str) -> bool:
    rc, _, stderr = run(["id", username])
    if rc == 0:
        return True

    assert "no such user" in stderr
    return False


def user_primary_group_id(user: str) -> int:
    return int(check(["id", "--group", user]))


def user_uid(user: str) -> int:
    return int(check(["id", "--user", user]))


def ensure_permissions(path: str, mode: int) -> bool:
    current = os.stat(path).st_mode
    current &= 0o777

    if current != mode:
        log("setting mode", path, oct(mode), oct(current))
        os.chmod(path, mode)
        return True

    return False


def ensure_owner(path: str, uid: int, gid: int) -> bool:
    st = os.stat(path)
    # current_uid = st_uid=501, st_gid=501,
    current_uid = st.st_uid
    current_gid = st.st_gid

    if current_uid != uid or current_gid != gid:
        log("changing owner", path, uid, gid)
        os.chown(path, uid, gid)
        return True

    return False


def ensure_link(src: str, dst: str) -> None:
    if not os.path.exists(dst):
        os.symlink(src=src, dst=dst)  # type: ignore

    if not os.path.islink(dst):
        raise NotImplementedError("Link changing not implemented")

    if os.readlink(dst) != src:
        raise NotImplementedError("Link changing not implemented")


def has_line(filename: str, line: str) -> bool:
    assert "\n" not in line
    with open(filename) as fp:
        content = fp.read()
    lines = content.splitlines(keepends=False)
    return line in lines


def ensure_line_in_file(filename: str, line: str, add_newline: bool = True) -> None:
    assert "\n" not in line
    nl = "\n" if add_newline else ""
    if not has_line(filename, line):
        log("adding line")
        with open(filename, "a") as fp:
            fp.write(line + nl)


def ensure_dir(
        path: str,
        mode: int,
        user: str,
        group: str,
) -> None:
    uid = getpwnam(user).pw_uid
    gid = getgrnam(group).gr_gid

    return _ensure_dir(
        path=path,
        mode=mode,
        uid=uid,
        gid=gid,
    )


def _ensure_dir(
        path: str,
        mode: int,
        uid: Optional[int] = None,
        gid: Optional[int] = None,
) -> None:
    if uid is None or gid is None:
        _, uid, gid = getuser()

    if not os.path.exists(path):
        os.mkdir(path, mode=mode)
    ensure_permissions(path, mode)
    ensure_owner(path, uid, gid)


def ensure_file(
        path: str,
        mode: int,
        user: str,
        group: str,
        content: str,
) -> bool:
    uid = getpwnam(user).pw_uid
    gid = getgrnam(group).gr_gid

    return _ensure_file(
        path=path,
        mode=mode,
        uid=uid,
        gid=gid,
        content=content.encode() if content is not None else None,
    )


def _ensure_file(
        path: str,
        mode: int,
        uid: Optional[int] = None,
        gid: Optional[int] = None,
        content: Optional[bytes] = None,
) -> bool:
    mut = False

    if uid is None or gid is None:
        _, uid, gid = getuser()

    if not os.path.exists(path):
        mut = True
        with open(path, "wb"):
            pass

    # TODO: if we set read-only here, we can't write the file below
    mut |= ensure_permissions(path, mode)
    mut |= ensure_owner(path, uid, gid)

    # TODO: check if permissions actually changed

    if content is None:
        return mut

    assert isinstance(content, bytes)

    with open(path, "rb") as fp:
        existing_content = fp.read()

    if existing_content == content:
        return mut

    with open(path, "wb") as fp:
        mut = True
        fp.write(content)

    return mut


def authorized_key(user: str, key_line: str) -> None:
    key_line = key_line.strip()
    home = os.path.expanduser(f"~{user}")
    log(home)

    ssh_dir = os.path.join(home, ".ssh")
    keys_file = os.path.join(ssh_dir, "authorized_keys")

    gid = user_primary_group_id(user)
    uid = user_uid(user)

    log(f"uid = {uid}, gid = {gid}")

    _ensure_dir(ssh_dir, 0o700, uid, gid)
    _ensure_file(keys_file, 0o600, uid, gid)

    ensure_line_in_file(keys_file, key_line)


def delete_password(user: str) -> None:
    output = check(["passwd", "--status", user])
    parts = output.split()
    assert parts[0] == user

    if parts[1] == "L":
        return

    elif parts[1] in ("P", "NP"):
        log("deleting password")
        check(["passwd", "-l", user])

    else:
        raise RuntimeError("Unexpected password status")


# def run_as(user: str, func: Callable, **kwargs):
#     # TODO: combine with other such things
#     msg = dict(
#         method=func.__name__,
#         params=kwargs,
#     )
#
#     step_payload = b64encode(pickle.dumps(msg, 0)).decode()
#
#     log("args", sys.argv)
#
#     parent_user = check(["id", "--user", "--name"])
#     parent_home = os.path.expanduser(f"~{parent_user}")
#
#     remote_scripts = __file__
#
#     args = ["sudo", "-u", user, "python3", remote_scripts, "rpc-step", step_payload]
#     log("abc123", " ".join(args))
#
#     home = os.path.expanduser(f"~{user}")
#     with cd(home):
#         subprocess.check_output(args)


def add_known_host(user: str, key_line: str) -> None:
    gid = user_primary_group_id(user)
    uid = user_uid(user)
    home = os.path.expanduser(f"~{user}")
    known_hosts = os.path.join(home, ".ssh", "known_hosts")
    _ensure_file(known_hosts, 0o600, uid, gid)
    ensure_line_in_file(known_hosts, key_line)


def add_user_to_group(user: str, group: str) -> None:
    text = check(["groups", user])
    groups = text.split()
    if group in groups:
        return
    log(f"adding {user} to {group}")
    check(["/usr/sbin/usermod", user, "-a", "-G", group])


def template(user: str, filename: str, content: str, mode: int) -> bool:
    gid = user_primary_group_id(user)
    uid = user_uid(user)
    return _ensure_file(filename, mode, uid, gid, content.encode())


def systemd(service_name: str, service_filename: str, service_content: str, mode: int) -> None:
    mut = template(
        user="root",
        filename=service_filename,
        content=service_content,
        mode=mode,
    )

    if mut or True:  # TODO!
        # TODO: ensure running or similar
        check(["systemctl", "daemon-reload"])
        check(["systemctl", "enable", service_name])
        check(["systemctl", "restart", service_name])

    else:
        check(["systemctl", "restart-or-reload", service_name])


def systemctl_enable(service_name: str) -> None:
    # enables, but does not run now
    check(["systemctl", "daemon-reload"])
    check(["systemctl", "enable", service_name])


def systemctl_disable(service_name: str) -> None:
    # enables, but does not run now
    check(["systemctl", "disable", service_name])
    check(["systemctl", "stop", service_name])


def systemctl_restart_if_running(service_name: str) -> None:
    output = check(["systemctl", "show", "--no-page", service_name])
    lines = output.splitlines(keepends=False)
    info = dict(line.split("=", maxsplit=1) for line in lines)
    if info["ActiveState"] == "active":
        log("restarting already running", service_name)
        check(["systemctl", "restart", service_name])


def getuser(user: Optional[str] = None) -> Tuple[str, int, int]:
    user_arg = [user] if user is not None else []
    user = check(["id", "--user", "--name"] + user_arg)
    uid = user_uid(user)
    gid = user_primary_group_id(user)

    assert isinstance(user, str)
    assert isinstance(uid, int)
    assert isinstance(gid, int)
    assert uid > 0 or (user == "root" and uid == 0)
    assert gid > 0 or (user == "root" and gid == 0)

    return user, uid, gid


def new_user_setup(
        user: str,
        authorized_keys: List[str],
        groups: List[str],
) -> None:
    log(f"setting up a new user: {user}")

    if not has_user(user):
        useradd = find_program("useradd", "/usr/sbin")
        shell = find_program("bash", "/bin")
        assert user is not None
        assert useradd is not None
        assert shell is not None
        cmd = [useradd, user, "--user-group", "--shell", shell, "--create-home"]
        check(cmd)

    for key_line in authorized_keys:
        authorized_key(user, key_line)

    delete_password(user)

    for group in groups:
        add_user_to_group(user, group)


def phase_2_setup(
        known_hosts: List[str],
        aliases: str,
        ssh_config: str,
) -> None:
    log("phase_2_setup")
    user = check(["id", "--user", "--name"])

    gid = user_primary_group_id(user)
    uid = user_uid(user)
    for host in known_hosts:
        add_known_host(user, host)

    log("uid = ", os.getuid())
    _ensure_file(".alias", 0o600, uid, gid, aliases.encode())
    ensure_link(".alias", ".bash_aliases")

    _ensure_file(".ssh/config", 0o600, uid, gid, ssh_config.encode())

    _ensure_dir("etc", 0o755, uid, gid)  # TODO: ability to opt in/out of 0o005
    _ensure_dir("bin", 0o750, uid, gid)


def get_info(user: str) -> Dict[str, str]:
    home = os.path.expanduser(f"~{user}")
    log("home", home)
    assert os.path.basename(home) == user
    user_home = os.path.dirname(home)

    machine = check(["uname", "-m"])

    return dict(
        user_home=user_home,
        machine=machine,
    )


def systemctl_reload(service: str) -> None:
    check(["systemctl", "reload", service])


def install_deb(url: str, digest: str, pkg_name: str, version: str) -> None:
    rc, output = subprocess.getstatusoutput(f"dpkg-query --show -f '${{Version}}' {pkg_name}")
    if rc == 0:
        have = output.strip()
        if have == version:
            return
        else:
            raise NotImplementedError(
                f"We don't support changing the version at the moment. Have={have} Want={version}")

    with tempfile.TemporaryDirectory() as tmpdir:
        with cd(tmpdir):
            filename = build_utils.fetch_archive(digest, url)
            check(
                ["apt-get", "install", "./" + filename],
                env={"DEBIAN_FRONTEND": "noninteractive"}
            )


def setup_host(hostname: str) -> None:
    current_hostname = platform.node()
    if hostname != current_hostname:
        check(["hostnamectl", "set-hostname", hostname])

    ensure_line_in_file(
        filename="/etc/hosts",
        line=f"127.0.0.1\t{hostname}",
    )

    # TODO: check before setting
    check(["timedatectl", "set-timezone", "America/Los_Angeles"])


def get_machine() -> str:
    return check(["uname", "-m"])


def install_packages(packages: List[str]) -> None:
    to_install = []
    for pkg in packages:
        rc, output = subprocess.getstatusoutput(f"dpkg-query --show -f '${{Status}}' {pkg}")
        log(pkg, output)
        if rc == 0:
            if "deinstall" in output:
                pass

            elif "not-installed" in output:
                pass

            elif "installed" in output:
                continue

            else:
                raise RuntimeError("Unexpected package state")
        to_install.append(pkg)

    if to_install:
        check(["apt-get", "update", "--allow-releaseinfo-change"], env={"DEBIAN_FRONTEND": "noninteractive"})
        check(["apt-get", "update"], env={"DEBIAN_FRONTEND": "noninteractive"})
        check(
            ["apt-get", "install", "-y", "--autoremove=no", *to_install],
            env={
                "DEBIAN_FRONTEND": "noninteractive",
                "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            },

        )


def new_git_repo(path: str) -> None:
    if not os.path.exists(path):
        with util.umask(0o027):  # TODO: consider making this a parameter
            check(["git", "init", "--bare", path])
