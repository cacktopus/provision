from typing import Dict, List, Optional

from .service import Service


class Timesync(Service):
    name = "timesync"
    description = "RTC and time syncing microservice"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c"]

    def command_line(self) -> str:
        return self.exe()

    def setup(self) -> None:
        self.get_tar_archive()

    def has_rtc(self) -> bool:
        return 'rtc' in self.ctx.record.tags

    def capabilities(self) -> List[str]:
        return ["CAP_SYS_TIME"]

    def start_after(self) -> str:
        return "network.target"

    def systemd_extra(self) -> Optional[Dict[str, str]]:
        return {
            "Type": "notify",
        }
