from provision.service import Service


class Syncthing(Service):
    name = "syncthing"
    description = "syncthing"
    deps = ["consul"]

    metrics_port = None

    def command_line(self) -> str:
        return None

    # TODO: health checks, etc.
    # TODO: monitoring

    def setup(self) -> None:
        # self.get_tar_archive()
        pass

    def register_mdns(self) -> None:
        pass
