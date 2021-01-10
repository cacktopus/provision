from typing import List, Dict

from .service import Service


class Head(Service):
    name = "head"
    description = "motor for head"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c", "gpio"]

    def env(self) -> Dict[str, str]:
        instance = self.ctx.record.kv['head']
        return {
            "GIN_MODE": "release",
            "INSTANCE": instance,
        }

    def command_line(self) -> str:
        return self.exe()

    def working_dir(self) -> str:
        return self.prod_path()

    def setup(self) -> None:
        self.get_tar_archive()

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="dtparam=i2c_arm=on",
        ))

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/etc/modules",
            line="i2c-dev",
        ))

    def mdns_service_name(self):
        instance = self.ctx.record.kv['head']
        return instance
