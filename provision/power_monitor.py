from typing import List

from .service import Service
from .systemd import ServiceConfig, BaseConfig


class PowerMonitor(Service):
    name = "power-monitor"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c"]

    def setup(self) -> None:
        self.get_tar_archive()
        self.enable_i2c()

    def systemd_args(self) -> BaseConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="power monitoring microservice",
        )
