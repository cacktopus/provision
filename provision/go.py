from .service import Provision


class Go(Provision):
    name = "go"
    deps = ["consul"]

    def setup(self) -> None:
        self.get_tar_archive()
