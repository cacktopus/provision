import distutils.util
from typing import List

from .service import Service
from .systemd import ServiceConfig, BaseConfig


class Leds(Service):
    name = "leds"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return ["build"]

    def setup(self) -> None:
        self.get_tar_archive()

        if self.has_ir():
            self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
                filename="/boot/config.txt",
                line="dtoverlay=gpio-ir,gpio_pin=4",  # TODO: allow config? (enable, pin#)
            ))

    def systemd_args(self) -> BaseConfig:
        config = ServiceConfig(
            exec_start="+" + self.exe(),  # run as root,
            description="led animations",
            env=self.ctx.record.env['leds'],
        )

        return config

    def has_ir(self) -> bool:
        env = self.ctx.record.env.get('leds', {})
        enable = env.get('ENABLE_IR', "0")

        return distutils.util.strtobool(enable)
