from .service import Service
from .systemd import ServiceConfig


class PrometheusDiscovery(Service):
    name = "prometheus-discovery"
    description = "service discovery for prometheus"
    deps = ["prometheus"]
    user = "prometheus"
    group = "prometheus"
    port = None

    def command_line(self) -> str:
        return

    def setup(self) -> None:
        self.get_tar_archive(pkg_name="system-tools")

    def systemd_args(self) -> ServiceConfig:
        start = " ".join([
            self.build_home("builds", "system-tools", "prod", "system-tools"),
            "discover-prometheus",
        ])

        return ServiceConfig(
            exec_start=start,
            description="service discovery for prometheus",
            type="simple",
            after=["network.target"],
            env={
                "OUTPUT_DIR": self.home_for_user("prometheus", "etc", "services"),
            }
        )
