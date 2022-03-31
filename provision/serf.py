import json
from typing import Optional

from .service import Service
from .systemd import ServiceConfig


class Serf(Service):
    name = "serf"
    deps = ["consul"]
    port = None

    def systemd_args_new(self) -> ServiceConfig:
        start = " ".join([
            self.exe(),
            "agent",
            "-config-dir", self.user_home("serf-cfg"),
        ])

        return ServiceConfig(
            exec_start=start,
            description="hashicorp serf",
            type="simple",
            after=["network.target"],
        )

    def setup(self) -> None:
        port = self.ctx.settings.serf.port

        hosts = [
            f"{host}:{port}"
            for host in self.ctx.settings.get_host_names_by_tag("serf")
        ]

        cfg = {
            "interface": self.ctx.record.primary_interface,
            "bind": f"0.0.0.0:{port}",
            "retry_join": hosts,
            "tags": {
                "cluster": self.ctx.settings.serf.cluster_name,
                "role": self.ctx.record.role,
            },
        }

        self.ensure_dir(
            path=self.user_home("serf-cfg"),
            mode=0o750,
            user=self.user,
            group=self.group,
        )

        self.ensure_file(
            path=self.user_home("serf-cfg", "serf.json"),
            mode=0o640,
            user=self.user,
            group=self.group,
            content=json.dumps(cfg, indent=4)
        )

        self.get_tar_archive()

    def register_mdns(self) -> None:
        pass
