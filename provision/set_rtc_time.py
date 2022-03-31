from provision.systemd import ServiceConfig
from typing import List, Optional

from .service import Service


class SetRTCTime(Service):
    name = "set-rtc-time"
    user = "timesync"
    deps = ["service-ready"]
    port = None

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c"]

    def setup(self) -> None:
        self.get_tar_archive(pkg_name="timesync")

    def systemd_args(self) -> ServiceConfig:
        cmd = " ".join([
            self.build_home("builds", "timesync", "prod", "timesync"),
            "--set-rtc-time",
        ])

        return ServiceConfig(
            exec_start=cmd,
            description="Set system clock to rtc",
            type="oneshot",
            remain_after_exit="yes",
            capabilities=["CAP_SYS_TIME"],
            after=["hwclock.service", "local-fs.target"],
        )
