from provision.service import Service


class Syncthing(Service):
    name = "syncthing"
    description = "syncthing"
    deps = ["consul"]

    def command_line(self) -> str:
        return " ".join([
            self.exe(),
            "-no-restart",
        ])

    # TODO: health checks, etc.
    # TODO: monitoring

    def setup(self) -> None:
        self.get_tar_archive()
