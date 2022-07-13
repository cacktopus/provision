from .service import Service
from .systemd import ServiceConfig, BaseConfig


class PrometheusDiscovery(Service):
    name = "prometheus-discovery"
    description = "service discovery for prometheus"
    deps = ["prometheus"]
    user = "prometheus"
    group = "prometheus"
    port = None

    def setup(self) -> None:
        self.get_tar_archive(pkg_name="system-tools")

    def systemd_args(self) -> BaseConfig:
        start = " ".join([
            self.build_home("builds", "system-tools", "prod", "system-tools"),
            "discover-prometheus",
        ])

        return ServiceConfig(
            exec_start=start,
            description="service discovery for prometheus",
            env={
                "OUTPUT_DIR": self.home_for_user("prometheus", "etc", "services"),
            }
        )
