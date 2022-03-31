from .service import Service
from .systemd import ServiceConfig


class NodeExporter(Service):
    name = "node-exporter"
    deps = ["service-ready"]

    def setup(self) -> None:
        self.get_tar_archive()

    def systemd_args(self) -> ServiceConfig:
        start = " ".join([
            self.prod_path("node_exporter"),
            "--collector.wifi",
        ])

        return ServiceConfig(
            exec_start=start,
            description="system stats exporter for prometheus monitoring tool",
            type="simple",
            after=["network.target"],
        )
