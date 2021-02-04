from .service import Provision


class Ubuntu(Provision):
    name = "ubuntu"
    deps = ["user(pi)"]

    def setup(self) -> None:
        self.runner.run_remote_rpc(
            "ubuntu_setup",
            params=dict(),
        )
