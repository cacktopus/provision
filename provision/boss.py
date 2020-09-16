from typing import List

from .service import Service


class Boss(Service):
    name = "boss"
    description = "The heads' boss"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["systemd-journal"]

    def working_dir(self) -> str:
        return self.prod_path()

    def command_line(self) -> str:
        lock = "boss-service-lock"
        cmd = self.exe()

        return f"/home/build/builds/consul/prod/consul lock -child-exit-code {lock} {cmd}"

    def register_for_monitoring(self) -> None:
        pass

    def setup(self) -> None:
        self.get_tar_archive()
        self.service_level_monitoring()
