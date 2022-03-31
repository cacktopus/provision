from .service import Provision


class Go(Provision):
    name = "go"
    deps = ["serf"]

    def setup(self) -> None:
        self.get_tar_archive()
