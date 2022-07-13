from typing import List

from .service import Service
from .systemd import ServiceConfig, BaseConfig


class Camera(Service):
    name = "camera"
    deps = ["service-ready", "opencv"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["video", "gpio"]

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

    def systemd_args(self) -> BaseConfig:
        return ServiceConfig(
            exec_start=self.prod_path("camera"),
            description="the eyes",
            working_dir=self.prod_path(),
        )

    def instance_name(self) -> str:
        # consider moving this out of provision/serf and into the app itself
        return self.ctx.record.env["camera"]["INSTANCE"]
