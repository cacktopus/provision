from typing import List

from .service import Service


class Home(Service):
    name = "home"
    description = "the home page (reverse proxy)"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + [
            "video",  # to turn off HDMI
        ]

    def capabilities(self) -> List[str]:
        return ["CAP_NET_BIND_SERVICE"]

    def command_line(self) -> str:
        return self.exe()

    def setup(self) -> None:
        self.get_tar_archive()

        for led in "led0", "led1":
            self.runner.run_remote_rpc("ensure_file", dict(
                path=f"/sys/class/leds/{led}/brightness",
                mode=0o660,
                user="root",
                group="home",  # TODO: perhaps a separate group
                content=None,
            ))
