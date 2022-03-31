from .service import Provision


class Syncthing(Provision):
    name = "syncthing"
    deps = ["user(build)", "packages2"]

    metrics_port = None

    def setup(self) -> None:
        # self.get_tar_archive()
        pass

    def register_mdns(self) -> None:
        pass
