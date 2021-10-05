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
            "-discover", "heads",
            "-snapshot", self.etc("serf.snapshot"),
        ])

    def setup(self) -> None:
        self.get_tar_archive()

    def register_mdns(self) -> None:
        pass
