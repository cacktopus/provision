import subprocess

from .service import Provision


class Packages(Provision):
    name = "packages"
    deps = ["start", "ubuntu"]

    def setup(self) -> None:
        opencv = [
            "build-essential",
            "cmake",
            "curl",
            "git",
            "libavcodec-dev",
            "libavformat-dev",
            "libdc1394-22-dev",
            "libgtk2.0-dev",
            "libjpeg-dev",
            "libpng-dev",
            "libswscale-dev",
            "libtbb-dev",
            "libtbb2",
            "libtiff-dev",
            "pkg-config",
            "unzip",
        ]

        packages = [
            "avahi-daemon",
            "curl",
            "dnsutils",
            "gcc",
            "git",
            "i2c-tools",
            "ifupdown",
            "iptables",
            "iptables-persistent",
            "ir-keytable",
            "jq",
            "libatlas3-base",
            "libffi-dev",
            "libusb-dev",
            "netfilter-persistent",
            "python3-dev",
            "python3-virtualenv",
            "rsync",
            "sudo",
            "tmux",
            "vim",
            "wavemon",
            "zip",
        ]

        package_list = opencv + packages

        self.runner.run_remote_rpc("install_packages", params=dict(packages=package_list))


class Packages2(Provision):
    name = "packages2"
    deps = ["packages"]

    def setup(self) -> None:
        package_list = [
            "autoconf",
            "automake",
            "avahi-daemon",
            "avahi-daemon",
            "avahi-utils",
            "build-essential",
            "ffmpeg",
            "git",
            "i2c-tools",
            "jq",
            "libasound2-dev",
            "libavahi-client-dev",
            "libconfig-dev",
            "libdaemon-dev",
            "libpopt-dev",
            "libssl-dev",
            "libtool",
            "mpg123",
            "python3-venv",
            "xmltoman",
        ]

        self.runner.run_remote_rpc("install_packages", params=dict(packages=package_list))


class SetupHost(Provision):
    name = "setup-host"
    deps = ["user(build)"]

    def setup(self) -> None:
        self.runner.run_remote_rpc("setup_host", params=dict(hostname=self.ctx.host))


class SyncStatic(Provision):
    name = "sync-static"
    deps = ["syncthing"]

    def setup(self) -> None:
        static = self.ctx.settings.static_files_path
        assert static
        record = self.ctx.record
        ip = record.initial_ip or record.host + ".local"  # TODO: this is duplicated

        cmd = f"rsync -av {static}/ syncthing@{ip}:"
        print(f"running {cmd}")

        retcode = subprocess.call(cmd, shell=True)
