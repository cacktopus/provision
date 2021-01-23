from typing import List, Dict

from .service import Service


class Boss(Service):
    name = "boss"
    description = "The heads' boss"
    deps = ["service-ready"]
    repo = "heads"

    def env(self) -> Dict[str, str]:
        return {
            "SCENE_PATH": "/home/syncthing/theheads/scenes/hb2021"
        }

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["systemd-journal"]

    def working_dir(self) -> str:
        return self.prod_path()

    def command_line(self) -> str:
        return self.exe()

    def setup(self) -> None:
        self.get_tar_archive()
        # self.service_level_monitoring()
