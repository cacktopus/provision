from .service import Service
from .systemd import ServiceConfig, BaseConfig


class NodeExporter(Service):
    name = "node-exporter"
    deps = ["service-ready"]

    def setup(self) -> None:
        self.get_tar_archive()

    def systemd_args(self) -> BaseConfig:
        start = " ".join([
            self.prod_path("node_exporter"),
            "--collector.wifi",
        ])

        return ServiceConfig(
            exec_start=start,
            description="system stats exporter for prometheus monitoring tool",
        )
