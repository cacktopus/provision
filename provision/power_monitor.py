from typing import List

from .service import Service
from .systemd import ServiceConfig


class PowerMonitor(Service):
    name = "power-monitor"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c"]

    def setup(self) -> None:
        self.get_tar_archive()

    def systemd_args(self) -> ServiceConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="power monitoring microservice",
            type="simple",  # TODO: notify?
            after=["network.target"],
        )
