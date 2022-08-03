from typing import List

from provision.systemd import OneshotConfig, BaseConfig
from .service import Service


class SetSystemTime(Service):
    name = "set-system-time"
    user = "timesync"
    deps = ["service-ready"]
    port = None

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c"]

    def setup(self) -> None:
        self.enable_i2c()
        self.get_tar_archive()

    def systemd_args(self) -> BaseConfig:
        return OneshotConfig(
            exec_start=self.exe(),
            description="Set system clock to rtc",
            remain_after_exit="yes",
            capabilities=["CAP_SYS_TIME"],
            after=["hwclock.service", "local-fs.target"],
            wanted_by=["basic.target"],
        )
