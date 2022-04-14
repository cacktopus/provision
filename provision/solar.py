from typing import List

from .service import Service
from .systemd import ServiceConfig


class Solar(Service):
    name = "solar"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["dialout"]

    def setup(self) -> None:
        # TODO: install kernel driver

        self.get_tar_archive()

    def systemd_args(self) -> ServiceConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="solar monitoring microservice",
            type="simple",  # TODO: notify?
            after=["network.target"],
        )
