from typing import List

from .service import Service


class PowerMonitor(Service):
    name = "solar"
    description = "solar monitoring microservice"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["dialout"]

    def command_line(self) -> str:
        return self.exe()

    def setup(self) -> None:
        # TODO: install kernel driver

        self.get_tar_archive()
