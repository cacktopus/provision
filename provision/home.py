from typing import List

from .service import Service


class Home(Service):
    name = "home"
    description = "the home page (reverse proxy)"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups()  # + ["git"]  # TODO: only if git enabled on server

    def capabilities(self) -> List[str]:
        return ["CAP_NET_BIND_SERVICE"]

    def command_line(self) -> str:
        return f"{self.prod_path()}/home/home"

    def setup(self) -> None:
        self.build()
