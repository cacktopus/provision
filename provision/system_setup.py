import subprocess

from .service import Provision


class Packages(Provision):
    name = "packages"
    deps = ["setup-host"]

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
            "build-essential",
            "ffmpeg",
            "git",
            "i2c-tools",
            "jq",
            "libasound2-dev",
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
    deps = ["users-ready"]

    def setup(self) -> None:
        self.runner.run_remote_rpc("setup_host", params=dict(hostname=self.ctx.host))
