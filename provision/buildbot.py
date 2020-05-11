import yaml

from .clients import consul_kv
from .service import Service


class Builtbot(Service):
    name = "buildbot"
    user = "build"
    group = "build"
    description = "Build robot"
    deps = ["consul"]

    def command_line(self) -> str:
        return self.exe()

    def consul_http_health_check_path(self) -> str:
        return "/metrics"  # TODO: move to /health when available

    def setup(self) -> None:
        self.get_tar_archive()

        for repo in self.ctx.settings.repos:
            consul_kv.put(
                path=f"buildbot/repos/{repo.name}.yaml",
                data=yaml.dump({
                    "name": repo.name,
                    "url": repo.url,
                }, default_flow_style=False)
            )
