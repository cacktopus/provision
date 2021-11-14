import subprocess

from .service import Provision


class Packages(Provision):
    name = "packages"
    deps = ["start", "ubuntu"]

    def setup(self) -> None:
        # opencv = [
        #     "unzip",
        #     "build-essential",
        #     "cmake",
        #     "curl",
        #     "git",
        #     "libgtk2.0-dev",
        #     "pkg-config",
        #     "libavcodec-dev",
        #     "libavformat-dev",
        #     "libswscale-dev",
        #     "libtbb2",
        #     "libtbb-dev",
        #     "libjpeg-dev",
        #     "libpng-dev",
        #     "libtiff-dev",
        #     "libdc1394-22-dev",
        # ]

        # package_list = [
        #     "wavemon",
        #     "tmux",
        #     "rsync",
        #     "git",
        #     "jq",
        #     "sudo",
        #     "python3-virtualenv",
        #     "curl",
        #     "vim",
        #     "dnsutils",
        #     "libatlas3-base",
        #     "zip",
        #     "ifupdown",
        #     "gcc",
        #     "python3-dev",
        #     "libffi-dev",
        #     "i2c-tools",
        #     "libusb-dev",
        #     "redis-server",
        #     "ir-keytable",
        #     *opencv,
        # ]

        package_list = [
            "avahi-daemon",
        ]

        self.runner.run_remote_rpc("install_packages", params=dict(packages=package_list))


class Packages2(Provision):
    name = "packages2"
    deps = ["packages"]

    def setup(self) -> None:
        package_list = [
            "ffmpeg",
            "avahi-utils",
            "autoconf",
            "automake",
            "avahi-daemon",
            "build-essential",
            "git",
            "libasound2-dev",
            "libavahi-client-dev",
            "libconfig-dev",
            "libdaemon-dev",
            "libpopt-dev",
            "libssl-dev",
            "libtool",
            "xmltoman",
            "mpg123",
            "python3-venv",
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

        retcode = subprocess.call(cmd, shell=True)
