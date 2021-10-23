from .service import Service


class Serf(Service):
    name = "serf"
    description = "hashicorp serf"
    deps = ["syncthing"]
    port = None

    def command_line(self) -> str:
        return " ".join([
            self.exe(),
            "agent",
            "-discover", self.ctx.settings.serf.cluster_name,
            # "-snapshot", self.etc("serf.snapshot"),
            "-bind", f"0.0.0.0:{self.ctx.settings.serf.port}",
            "-tag", f"cluster={self.ctx.settings.serf.cluster_name}",
        ])

    def setup(self) -> None:
        self.get_tar_archive()

    def register_mdns(self) -> None:
        pass
