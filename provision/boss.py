from typing import List

from .service import Service


class Boss(Service):
    name = "boss"
    description = "The heads' boss"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["systemd-journal"]

    def working_dir(self) -> str:
        return self.prod_path()

    def command_line(self) -> str:
        lock = "boss-service-lock"
        cmd = self.prod_path("boss", "boss")

        return f"/home/build/builds/consul/prod/consul lock -child-exit-code {lock} {cmd}"

    def register_for_monitoring(self) -> None:
        pass

    def setup(self) -> None:
        self.build()
        self.service_level_monitoring()
