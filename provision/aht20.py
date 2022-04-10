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
        self.enable_i2c()

    def systemd_args(self) -> ServiceConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="aht20 temperature and humidity sensor",
            type="simple",  # TODO: notify?
            after=["network.target"],
        )
