from .service import Service


class NodeExporter(Service):
    name = "node-exporter"
    description = "system stats exporter for prometheus monitoring tool"
    deps = ["consul"]

    def command_line(self) -> str:
        return " ".join([
            self.prod_path("node_exporter"),
            "--collector.wifi",
            "--collector.systemd",
            "--collector.systemd.unit-whitelist='firewall.service|consul-template.service'"
        ])

    def setup(self) -> None:
        self.get_tar_archive()
