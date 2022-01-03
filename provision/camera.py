from typing import List, Dict

from .service import Service


class Camera(Service):
    name = "camera"
    description = "heads' camera"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["video", "gpio"]

    def command_line(self) -> str:
        return f"{self.prod_path()}/camera"

    def working_dir(self) -> str:
        return self.prod_path()

    def setup(self) -> None:
        self.get_tar_archive()

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="start_x=1",
        ))

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="gpu_mem=64",
        ))

    def mdns_service_name(self):
        return self.ctx.record.env['camera']['INSTANCE']
