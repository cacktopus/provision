from typing import List, Dict

from .service import Service


class Head(Service):
    name = "head"
    description = "motor for head"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c", "gpio"]

    def env(self) -> Dict[str, str]:
        instance = self.ctx.record['kv']['head']
        return {
            "INSTANCE": instance,  # TODO
        }

    def command_line(self) -> str:
        return " ".join([
            self.prod_path("env", "bin", "python3"),
            "head.py"
        ])

    def working_dir(self) -> str:
        return self.prod_path()

    def setup(self) -> None:
        self.build()

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="dtparam=i2c_arm=on",
        ))

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/etc/modules",
            line="i2c-dev",
        ))

    def register_service(self) -> None:
        head = self.ctx.record['kv']['head']
        assert self.port is not None
        self.register_service_with_consul(self.name, self.port, tags=["frontend", head])
