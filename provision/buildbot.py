from typing import Dict

from .service import Service


class Builtbot(Service):
    name = "buildbot"
    user = "build"
    group = "build"
    description = "Build robot"
    deps = ["consul"]

    def command_line(self) -> str:
        return self.exe()

    def env(self) -> Dict[str, str]:
        return {"GIT_URL": "git://git.service.consul/git/heads.git"}  # TODO: move to yaml

    def consul_http_health_check_path(self) -> str:
        return "/metrics"  # TODO: move to /health when available

    def setup(self) -> None:
        self.get_tar_archive()
