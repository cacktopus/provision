from typing import List

from .service import Service
from .systemd import ServiceConfig, BaseConfig


class Boss(Service):
    name = "boss"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["systemd-journal"]

    def command_line(self) -> str:
        return self.exe()

    def setup(self) -> None:
        self.get_tar_archive()

    def systemd_args(self) -> BaseConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="the heads' boss",
            working_dir=self.prod_path(),
        )
