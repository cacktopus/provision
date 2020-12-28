from typing import List

from .service import Service


class Home(Service):
    name = "home"
    description = "the home page (reverse proxy)"
    deps = ["service-ready"]
    repo = "heads"

    def capabilities(self) -> List[str]:
        return ["CAP_NET_BIND_SERVICE"]

    def command_line(self) -> str:
        return self.exe()

    def setup(self) -> None:
        self.get_tar_archive()
