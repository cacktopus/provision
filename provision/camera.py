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
        return f"{self.prod_path()}/camera"

    def env(self) -> Dict[str, str]:
        instance = self.ctx.record.kv['camera']
        return {
            "GIN_MODE": "release",
            "INSTANCE": instance,
            # "FILENAME": {
            #     "camera-01": "/home/syncthing/theheads/testdata/pi42.raw",
            #     "camera-02": "/home/syncthing/theheads/testdata/pi43.raw"
            # }[instance]
        }

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
        instance = self.ctx.record.kv['camera']
        return instance
