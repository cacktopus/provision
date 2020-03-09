from .service import Provision


class PythonEnv(Provision):
    name = "python-env"
    deps = ["consul"]

    def setup(self) -> None:
        self.build()
