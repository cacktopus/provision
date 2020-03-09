from typing import List, Dict

import provision.settings as settings
from .service import Service


class Leds(Service):
    name = "leds"
    description = "led animations"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return ["build", "spi", "input"]

    def command_line(self) -> str:
        return f"{self.prod_path()}/leds/leds"

    def env(self) -> Dict[str, str]:
        result: Dict[str, str] = settings.settings['env']['leds']

        host_env = self.ctx.record.get('env', {})
        leds_env = host_env.get('leds', {})

        result.update(leds_env)
        return result

    def setup(self) -> None:
        # TODO: require raspbian
        self.build()

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="dtparam=spi=on",
        ))

        # self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
        #     filename="/boot/config.txt",
        #     line="dtoverlay=gpio-ir,gpio_pin=21",
        # ))

        # TODO: sudo apt-get install ir-keytable
        # TODO: sudo ir-keytable -c -p nec
