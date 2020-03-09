from typing import List

from .service import Service


class ConsulTemplate(Service):
    name = "consul-template"
    description = "consul templating tool"
    deps = ["consul"]

    port = None

    def reload(self) -> str:
        return "/bin/kill -HUP $MAINPID"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["systemd-journal"]

    def command_line(self) -> str:
        tin = self.etc("prometheus-services.tpl")
        tout = self.etc("prometheus-services.yml")

        return " ".join([
            self.prod_path(self.name),
            "-vault-retry=false",
            "-vault-renew-token=false",
            "-kill-signal", "SIGTERM",
            "-template", f"{tin}:{tout}",
        ])

    def setup(self) -> None:
        self.get_tar_archive()

        with open("templates/prometheus-services.tpl") as f:
            content = f.read()

        self.ensure_file(
            path=self.etc("prometheus-services.tpl"),
            mode=0o644,  # TODO:
            user=self.user,
            group=self.group,
            content=content,
        )
