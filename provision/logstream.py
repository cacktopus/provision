from .service import Service
from .systemd import ServiceConfig


class Logstream(Service):
    name = "logstream"
    deps = ["service-ready"]

    def setup(self) -> None:
        self.get_tar_archive()

    def systemd_args(self) -> ServiceConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="log streaming microservice",
            type="simple",  # TODO: notify?
            after=["network.target"],
        )
