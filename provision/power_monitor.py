from .service import Service
from typing import List


class PowerMonitor(Service):
    name = "power-monitor"
    description = "power monitoring microservice"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c"]

    def command_line(self) -> str:
        return self.exe()

    def setup(self) -> None:
        self.get_tar_archive()
