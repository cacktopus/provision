from .service import Provision


class HeadsCLI(Provision):
    name = "heads-cli"
    description = "heads command line interface"
    deps = ["service-ready"]

    def setup(self) -> None:
        self.get_tar_archive()
