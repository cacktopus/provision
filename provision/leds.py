from typing import List

from .service import Service
from .systemd import ServiceConfig


class Leds(Service):
    name = "leds"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return ["build"]

    def setup(self) -> None:
        self.get_tar_archive()

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="dtoverlay=gpio-ir,gpio_pin=4",  # TODO: allow config? (enable, pin#)
        ))

    def systemd_args(self) -> ServiceConfig:
        return ServiceConfig(
            exec_start_pre="+/usr/bin/ir-keytable -c -p nec",
            exec_start="+" + self.exe(),  # run as root,
            description="led animations",
            type="simple",  # TODO: notify?
            after=["network.target"],
            env=self.ctx.settings.env['leds'],
        )
