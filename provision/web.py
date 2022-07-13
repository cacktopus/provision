from typing import List

from provision.systemd import ServiceConfig, BaseConfig

from .service import Service


class Web(Service):
    name = "web"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + [
            "video",  # to turn off HDMI
        ]

    def setup(self) -> None:
        self.get_tar_archive()
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

    def systemd_args(self) -> BaseConfig:
        # TODO: perhaps use a separate group here
        pre = "+/bin/bash -c 'chown web.web /sys/class/leds/led*/{brightness,trigger}'"

        return ServiceConfig(
            exec_start=self.exe(),
            description="web server (reverse proxy)",
            capabilities=["CAP_NET_BIND_SERVICE"],
            exec_start_pre=pre,
        )
