from .systemd import ServiceConfig
from typing import List, Optional

from .service import Service


class Timesync(Service):
    name = "timesync"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c"]

    def setup(self) -> None:
        self.get_tar_archive()

    def systemd_args(self) -> ServiceConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="RTC and time syncing microservice",
            type="notify",
            capabilities=["CAP_SYS_TIME"],
            after=["network.target"],
        )
