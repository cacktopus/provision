from typing import Dict, List

from .service import Service


class Leds(Service):
    name = "timesync"
    description = "RTC and time syncing microservice"
    deps = ["service-ready"]

    def command_line(self) -> str:
        return f"{self.prod_path()}/timesync/timesync"

    def env(self) -> Dict[str, str]:
        return {"RTC": "1"} if self.has_rtc() else {}

    def setup(self) -> None:
        self.build()

    def register_service(self) -> None:
        # TODO: have tags or extra_tags be a function rather than calling this
        tags = ['rtc'] if self.has_rtc() else []
        assert self.port is not None
        self.register_service_with_consul(self.name, self.port, tags=tags)

    def has_rtc(self) -> bool:
        return 'rtc' in self.ctx.record['tags']

    def capabilities(self) -> List[str]:
        return ["CAP_SYS_TIME"]
