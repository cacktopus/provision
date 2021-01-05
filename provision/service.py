import json
import os
from typing import List, Dict, Optional, Any, Tuple

import provision.packages as packages
import requests
import yaml
from jinja2 import Template

from .clients import consul_kv
from .consul_health_checks import check_http
from .context import Context
from .run_remote_script import Runner
from .service_util import adduser, template
from .systemd import systemd
from .users import CONSUL_USER


class Provision:
    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def user(self) -> str:
        raise NotImplementedError

    @property
    def group(self) -> str:
        return self.user

    @property
    def action_name(self) -> str:
        return self.name

    @property
    def deps(self) -> List[str]:
        raise NotImplementedError("Must specify dependencies")

    def __call__(self, ctx: Context) -> None:
        self.ctx = ctx
        self.info = Runner.get_info(self.ctx.root_conn)
        self.runner = Runner(self.ctx.root_conn)
        self.execute()

    def setup(self) -> None:
        raise NotImplementedError

    def execute(self) -> List[Dict[str, Any]]:
        self.setup()
        return self.runner.execute()

    def home_for_user(self, user: str, *other_paths: str) -> str:
        return os.path.join(self.info['user_home'], user, *other_paths)

    def build_home(self, *other_paths: str) -> str:
        return self.home_for_user("build", *other_paths)

    @property
    def repo(self) -> str:
        raise NotImplementedError

    def build(self) -> None:
        host = self.ctx.host
        service = self.name

        consul_kv.put(
            path=f"buildbot/instances/{host}/{service}",
            data="",
        )

        service_config_path = f"buildbot/service-config/{service}.yaml"
        if not consul_kv.has(service_config_path):
            repo_name = self.repo
            repo = self.ctx.settings.get_repo_by_name(repo_name)

            consul_kv.put(
                path=service_config_path,
                data=yaml.dump({
                    "repo": repo.name,
                    "version": repo.default_commit,
                }, default_flow_style=False)
            )

    def get_archive(self, kind: str, name: Optional[str] = None) -> None:
        cmd = f"get_{kind}_archive"
        machine = self.info['machine']
        pkg, arch = packages.latest_semver(name or self.name, machine)

        url = arch['url']
        url = Template(url).render(builds=self.ctx.settings.build_storage_url)

        self.runner.run_remote_rpc(cmd, params=dict(
            app_name=pkg['name'],
            url=url,
            digest=arch['digest'],
        ), user="build")

    def get_zip_archive(self) -> None:
        return self.get_archive("zip")

    def get_tar_archive(self, **kw) -> None:
        return self.get_archive("tar", **kw)

    def get_tar_bz_archive(self) -> None:
        return self.get_archive("tar_bz")

    def reload_consul(self) -> None:
        self.runner.run_remote_rpc("systemctl_reload", params=dict(service="consul"))

    def consul_health_checks(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def register_service_with_consul(
            self,
            name: str,
            port: int,
            tags: Optional[List[str]] = None,
            checks: Optional[List[Any]] = None,  # TODO: type this list
    ) -> None:
        raise NotImplementedError

        checks = checks or []
        assert isinstance(checks, list)
        name = name.replace("_", "-")

        location = self.home_for_user(CONSUL_USER, "consul.d", f"{name}.json")

        content = json.dumps({
            "service": {
                "name": name,
                "port": port,
                "tags": tags or [],
                "checks": self.consul_health_checks(),
            },
        }, sort_keys=True, indent=4)

        self.ensure_file(
            path=location,
            mode=0o644,
            user=CONSUL_USER,
            group=CONSUL_USER,
            content=content,
        )

        self.reload_consul()

    def ensure_file(
            self,
            path: str,
            mode: int,
            user: str,
            group: str,
            content: str,
    ) -> None:
        user = user or self.user
        self.runner.run_remote_rpc("ensure_file", params=dict(
            path=path,
            mode=mode,
            user=user,
            group=group,
            content=content,
        ))

    def ensure_dir(
            self,
            path: str,
            mode: int,
            user: str,
            group: str,
    ) -> None:
        user = user or self.user
        self.runner.run_remote_rpc("ensure_dir", params=dict(
            path=path,
            mode=mode,
            user=user,
            group=group,
        ))

    def template_vars(self) -> Dict[str, str]:
        return {}

    def template(
            self,
            name: str,
            location: str,
            user: str,
            group: str,
            vars: Optional[Dict[str, Any]] = None,
            mode: Optional[int] = 0o640,
            template_delimiters: Optional[Tuple[str, str]] = None
    ) -> None:
        vars = vars or self.template_vars()
        content = template(name, vars=vars, template_delimiters=template_delimiters)

        assert os.path.isabs(location), location

        assert mode is not None

        self.ensure_file(
            path=location,
            mode=mode,
            user=user,
            group=group,
            content=content,
        )

    def setup_sudo_for_build_restart(self) -> None:
        content = f"build ALL=(root) NOPASSWD: /bin/systemctl restart {self.name}\n"
        path = f"/etc/sudoers.d/099_restart-{self.name}"

        self.ensure_file(
            path=path,
            mode=0o640,  # TODO: 0x440,
            user="root",
            group="root",
            content=content,
        )


class Service(Provision):
    @property
    def user(self) -> str:
        return self.name

    @property
    def description(self) -> str:
        raise NotImplementedError

    @property
    def port(self) -> Optional[int]:
        return self.ctx.settings.ports[self.name]

    def extra_groups(self) -> List[str]:
        return ["build", "systemd-journal"]

    def env(self) -> Dict[str, str]:
        return {}

    def user_home(self, *other_paths: str) -> str:
        return os.path.join(self.info['user_home'], self.user, *other_paths)

    def etc(self, *other_paths: str) -> str:
        return self.user_home("etc", *other_paths)

    def config_dir(self, *other_paths: str) -> str:
        return self.etc(self.name, *other_paths)

    def prod_path(self, *other_paths: str) -> str:
        return os.path.join(self.build_home(), "builds", self.name, "prod", *other_paths)

    def exe(self) -> str:
        return self.prod_path(self.name)

    def working_dir(self) -> str:
        return self.user_home()

    def command_line(self) -> Optional[str]:
        raise NotImplementedError

    def capabilities(self) -> List[str]:
        return []

    def reload(self) -> Optional[str]:
        return None

    def register_service(self) -> None:
        if self.port is None:
            return

        # self.register_service_with_consul(self.name, self.port)

    def execute(self) -> List[Dict[str, Any]]:
        adduser(self.ctx, self.runner, self.user, self.extra_groups())

        self.setup()

        systemd_args = self.systemd_args()
        if systemd_args is not None:
            rendered = systemd(**systemd_args)
            rendered["mode"] = 0o644
            self.runner.run_remote_rpc("systemd", params=rendered)

        self.register_mdns()
        self.register_service()
        self.setup_sudo_for_build_restart()  # TODO: only needed for code we build from git

        return self.runner.execute()

    def systemd_extra(self):
        return None

    def systemd_args(self) -> Optional[Dict[str, Any]]:
        command_line = self.command_line()

        if command_line is None:
            return None

        return dict(
            service_name=self.name,
            user=self.user,
            description=self.description,
            exec_start=command_line,
            working_dir=self.working_dir(),
            group=self.group,
            env=self.env(),
            capabilities=self.capabilities(),
            reload=self.reload(),
            extra=self.systemd_extra(),
        )

    def consul_health_checks(self) -> List[Dict[str, Any]]:
        method, url = self.consul_http_health_check_url()
        return [check_http(service=self.name, method=method, url=url)]

    def consul_http_health_check_path(self) -> str:
        return "/health"

    def consul_http_health_check_url(self) -> Tuple[str, str]:
        host = self.ctx.host
        path = self.consul_http_health_check_path()
        assert path.startswith("/")
        return "GET", f"http://{host}.node.consul:{self.port}{path}"

    def metrics_path(self) -> Optional[str]:
        return None

    def metrics_params(self) -> Dict[str, str]:
        return {}

    @property
    def metrics_port(self) -> Optional[int]:
        return self.port

    def mdns_service_name(self) -> str:
        return f"{self.name} on %h"

    def register_mdns(self) -> None:
        kv = {}

        if self.metrics_port is not None:
            kv["prometheus_metrics_port"] = self.metrics_port

        txt_records = "\n".join(f"    <txt-record>{k}={v}</txt-record>" for (k, v) in kv.items())

        self.template(
            name="avahi.service",
            location=f"/etc/avahi/services/{self.name}.service",
            user="root",
            group="root",
            vars=dict(
                service_name=self.mdns_service_name(),
                service_type=self.name,
                port=self.port,
                txt_records=txt_records,
            ),
            mode=0o644,
        )

    def service_level_monitoring(self) -> None:
        raise NotImplementedError

        port = self.metrics_port

        if port is None:
            return

        filename = f"{self.name}.yaml"

        cfg = [{
            "targets": [f"{self.name}.service.consul:{port}"],
            "labels": {
                "job": self.name,
            }
        }]

        content = yaml.dump(cfg, default_flow_style=False)

        # consul_kv.put(
        #     path=f"prometheus/by-service/{filename}",
        #     data=content,
        # )
