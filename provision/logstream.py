from .service import Service
from .systemd import ServiceConfig, BaseConfig


class Logstream(Service):
    name = "logstream"
    deps = ["service-ready"]

    def setup(self) -> None:
        self.get_tar_archive()

    def systemd_args(self) -> BaseConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="log streaming microservice",
        )
