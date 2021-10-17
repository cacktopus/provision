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

        self._setup_sudo()

    def _setup_sudo(self):
        content = ""
        content += f"{self.user} ALL=(root) NOPASSWD: /sbin/shutdown -h now\n"
        content += f"{self.user} ALL=(root) NOPASSWD: /sbin/shutdown -r now\n"
        path = f"/etc/sudoers.d/099_halt_or_reboot"

        self.ensure_file(
            path=path,
            mode=0o440,  # TODO: 0x440,
            user="root",
            group="root",
            content=content,
        )


def systemd_extra(self):
    pre = "+chown home.home /sys/class/leds/led0/brightness /sys/class/leds/led1/brightness"
    return {"ExecStartPre": pre}
