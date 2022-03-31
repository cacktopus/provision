from typing import List, Optional

from .service import Service
from .systemd import ServiceConfig


class Head(Service):
    name = "head"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c", "gpio", "audio"]

    def working_dir(self) -> str:
        return self.prod_path()

    def setup(self) -> None:
        self.get_tar_archive()

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="dtparam=i2c_arm=on",
        ))

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/etc/modules",
            line="i2c-dev",
        ))

    def systemd_args_new(self) -> ServiceConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="this is the head",
            type="simple",  # TODO: notify?
            after=["network.target"],
        )

    def mdns_service_name(self):
        return self.ctx.record.env['head']['INSTANCE']
