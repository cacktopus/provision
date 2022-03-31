from typing import List

from .service import Service
from .systemd import ServiceConfig


class Aht20(Service):
    name = "aht20"
    description = "aht20 temperature and humidity sensor"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c"]

    def setup(self) -> None:
        self.get_tar_archive()

        # TODO: share this gpio enablement code
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
            description="aht20 temperature and humidity sensor",
            type="simple",  # TODO: notify?
            after=["network.target"],
        )
