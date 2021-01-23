from typing import Dict

from .service import Service


class PrometheusDiscovery(Service):
    name = "prometheus-discovery"
    description = "mdns discovery for prometheus"
    deps = ["prometheus"]
    user = "prometheus"
    group = "prometheus"
    repo = None
    port = None

    def command_line(self) -> str:
        return " ".join([
            self.build_home("builds", "system-tools", "prod", "system-tools"),
            "discover-prometheus",
        ])

    def env(self) -> Dict[str, str]:
        return {
            "OUTPUT_DIR": "etc/services",
        }

    def setup(self) -> None:
        self.get_tar_archive(name="system-tools")

    def register_mdns(self) -> None:
        pass
