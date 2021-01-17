from typing import Dict, List

from .service import Service


class Logstream(Service):
    name = "logstream"
    description = "log streaming microservice"
    deps = ["service-ready"]
    repo = "heads"

    def command_line(self) -> str:
        return self.exe()

    def setup(self) -> None:
        self.get_tar_archive()
