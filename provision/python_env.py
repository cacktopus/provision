from .service import Provision


class PythonEnv(Provision):
    name = "python-env"
    deps = ["consul"]
    repo = "heads"

    def setup(self) -> None:
        self.build()
