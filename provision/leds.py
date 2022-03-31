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
            line="dtparam=spi=on",
        ))

        # TODO: sudo apt-get install ir-keytable
        # TODO: sudo ir-keytable -c -p nec

    def systemd_args(self) -> ServiceConfig:
        return ServiceConfig(
            exec_start="+" + self.exe(),  # run as root,
            description="led animations",
            type="simple",  # TODO: notify?
            after=["network.target"],
            env=self.ctx.settings.env['leds'],
        )
