from typing import List, Dict

from .service import Service


class Camera(Service):
    name = "camera"
    description = "heads' camera"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["video"]

    def command_line(self) -> str:
        instance = self.ctx.record.kv['camera']
        return f"{self.prod_path()}/camera/camera --instance {instance}"

    def env(self) -> Dict[str, str]:
        return {
            "LD_LIBRARY_PATH": "/usr/local/lib",
        }

    def working_dir(self) -> str:
        return self.prod_path("camera")

    def setup(self) -> None:
        self.build()

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="start_x=1",
        ))

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="gpu_mem=64",
        ))

    def register_service(self) -> None:
        camera = self.ctx.record.kv['camera']
        assert self.port is not None
        self.register_service_with_consul(self.name, self.port, tags=["frontend", camera])
