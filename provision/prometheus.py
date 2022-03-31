from typing import Dict, List, Any, Optional

import yaml

from .service import Service
from .settings import Settings
from .systemd import ServiceConfig


class Prometheus(Service):
    name = "prometheus"
    deps = ["service-ready"]

    def reload(self) -> str:
        return "/bin/kill -HUP $MAINPID"

    def template_vars(self) -> Dict[str, str]:
        file_pattern = self.etc("services", "*.yml")
        return dict(cfg=build_prom_config(self.ctx.settings, file_pattern))

    def setup(self) -> None:
        self.get_tar_archive()

        self.ensure_dir(
            self.user_home("etc", "services"),
            mode=0o755,
            user=self.user,
            group=self.group,
        )

        self.template(
            name="prometheus.yml",
            location=self.user_home("etc", "prometheus.yml"),
            user=self.user,
            group=self.group,
        )

        self.template(
            name="alerts.yml",
            location=self.user_home("etc", "alerts.yml"),
            user=self.user,
            group=self.group,
            vars=dict(
                tags=self.ctx.settings.all_tags,
            ),
            template_delimiters=("((", "))"),
        )

    def systemd_args(self) -> ServiceConfig:
        start = " ".join([
            self.exe(),
            "--config.file", self.user_home("etc", "prometheus.yml"),
            "--storage.tsdb.path", self.user_home("prometheus_data")
        ])

        return ServiceConfig(
            exec_start=start,
            description="prometheus monitoring tool",
            type="simple",
            after=["network.target"],
        )


def static_config(settings: Settings, job_name: str, targets: Optional[List[Any]] = None, **kw: Any) -> Dict[str, Any]:
    targets = targets or settings.get_hosts(job_name)
    result = {
        "job_name": job_name,
        "static_configs": [
            {
                "targets": targets
            }
        ]
    }
    result.update(kw)
    return result


def config_header(alert_manager_targets: List[Any], scrape_configs: List[Any]) -> str:
    cfg = {
        "global": {
            "scrape_interval": "15s",
            "evaluation_interval": "15s",
        },
        "alerting": {
            "alertmanagers": [
                {
                    "static_configs": [
                        {
                            "targets": alert_manager_targets,
                        }
                    ]
                }
            ]
        },
        "rule_files": [
            "alerts.yml"
        ],
        "scrape_configs": scrape_configs
    }
    result: str = yaml.dump(cfg, default_flow_style=False)
    return result


def build_prom_config(settings: Settings, file_pattern: str) -> str:
    scrape_configs = [
        {
            "job_name": "dummy",
            "file_sd_configs": [
                {
                    "files": [file_pattern]
                }
            ]
        },
    ]

    cfg = config_header(
        alert_manager_targets=settings.get_hosts("alertmanager"),
        scrape_configs=scrape_configs,
    )
    return cfg
