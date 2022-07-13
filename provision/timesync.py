from typing import List

from .service import Service
from .systemd import ServiceConfig, BaseConfig


class Timesync(Service):
    name = "timesync"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c"]

    def setup(self) -> None:
        self.enable_i2c()
        self.get_tar_archive()

    def systemd_args(self) -> BaseConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="RTC and time syncing microservice",
            type="notify",
            capabilities=["CAP_SYS_TIME"],
        )
