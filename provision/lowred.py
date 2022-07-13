from typing import List

from .service import Service
from .systemd import OneshotConfig, BaseConfig


class Lowred(Service):
    name = "lowred"
    deps = ["service-ready"]
    port = None

    def extra_groups(self) -> List[str]:
        return ["build"]

    def setup(self) -> None:
        self.get_tar_archive()

    def systemd_args(self) -> BaseConfig:
        config = OneshotConfig(
            exec_start="+" + self.exe(),  # run as root,
            description="startup led illuminator",
            default_dependencies="no",
            wanted_by=["basic.target"],
        )

        return config
