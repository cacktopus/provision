from typing import Dict, Any

from .service import Service
from .systemd import ServiceConfig


class Grafana(Service):
    name = "grafana"
    deps = ["serf", "prometheus"]

    def systemd_args(self) -> Dict[str, Any]:
        args = super().systemd_args()
        assert args is not None
        args.update(working_dir=self.prod_path())
        return args

    def template_vars(self) -> Dict[str, str]:
        return dict(
            data_path=self.user_home("grafana_data"),
            provisioning_path=self.config_dir("provisioning")
        )

    def setup(self) -> None:
        self.get_tar_archive()

        # TODO: reset admin password

        for path in (
                self.config_dir(),
                self.config_dir("provisioning")
        ):
            self.ensure_dir(
                path=path,
                mode=0o750,
                user=self.user,
                group=self.group,
            )

        self.template(
            name="grafana/custom.ini",
            location=self.config_dir("custom.ini"),
            user=self.user,
            group=self.group
        )

        for name in ["datasources"]:
            self.ensure_dir(
                path=self.config_dir("provisioning", name),
                mode=0o750,
                user=self.user,
                group=self.group,
            )

            self.template(
                name=f"grafana/{name}.yml",
                location=self.config_dir("provisioning", name, f"{name}.yml"),
                user=self.user,
                group=self.group,
            )

    def systemd_args(self) -> ServiceConfig:
        start = " ".join([
            self.prod_path("bin", "grafana-server"),
            "--homepath", self.prod_path(),
            "--config", self.config_dir("custom.ini"),
        ])

        return ServiceConfig(
            exec_start=start,
            description="grafana dashboards",
            type="simple",
            after=["network.target"],
        )
