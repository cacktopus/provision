from typing import List, Dict

from .service import Service


class Leds(Service):
    name = "leds"
    description = "led animations"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return ["build"]

    def command_line(self) -> str:
        return "+" + self.exe()  # run as root

    def env(self) -> Dict[str, str]:
        result: Dict[str, str] = self.ctx.settings.env['leds']
        leds_env = self.ctx.record.env.get('leds', {})
        result.update(leds_env)
        return result

    def setup(self) -> None:
        self.get_tar_archive()

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="dtparam=spi=on",
        ))

        # TODO: sudo apt-get install ir-keytable
        # TODO: sudo ir-keytable -c -p nec
