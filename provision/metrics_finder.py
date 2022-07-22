from .service import Service
from .systemd import ServiceConfig, BaseConfig


class MetricsFinder(Service):
    name = "metrics-finder"
    deps = ["prometheus"]
    user = "prometheus"
    group = "prometheus"
    port = None

    def setup(self) -> None:
        self.get_tar_archive()

    def systemd_args(self) -> BaseConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="service discovery for metrics",
            env={
                "OUTPUT_DIR": self.home_for_user("prometheus", "etc", "services"),
            }
        )
