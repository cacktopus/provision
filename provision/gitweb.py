from typing import Dict, List

from .service import Service


class Gitweb(Service):
    name = "gitweb"
    user = "gitweb"
    group = "gitweb"
    description = "Simple CGI wrapper for git http-backend"
    deps = ["consul", "git"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["git"]

    def command_line(self) -> str:
        return self.exe()

    def setup(self) -> None:
        self.get_tar_archive()
