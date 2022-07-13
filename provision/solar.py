from typing import List

from .service import Service
from .systemd import ServiceConfig, BaseConfig


class Solar(Service):
    name = "solar"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["dialout"]

    def setup(self) -> None:
        # note: if the kernel is upgraded, this will have to be run again manually
        kernel = self.info["kernel"]

        self.get_tar_archive(pkg_name="xr_usb_serial_common")
        self.get_tar_archive()

        self.ensure_file(
            path="/etc/modprobe.d/blacklist-cdc-acm.conf",
            mode=0o644,
            user="root",
            group="root",
            content="blacklist cdc-acm"
        )

        self.build_home()

        self.runner.run_remote_rpc("copyfile", params={
            "src": self.build_home("builds", "xr_usb_serial_common", "prod", "xr_usb_serial_common.ko"),
            "dst": f"/usr/lib/modules/{kernel}",
        })

        self.runner.run_remote_rpc("depmod", params={})

        self.ensure_line_in_file(
            path="/etc/modules",
            line="xr_usb_serial_common",
        )

    def systemd_args(self) -> BaseConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="solar monitoring microservice",
        )
