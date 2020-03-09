import json
import os
from typing import List, Dict, Optional, Any, Tuple

import requests
import yaml

import provision.packages as packages
import provision.settings as settings
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

    # TODO: This is perhaps deprecated
    def repo(self) -> str:
        return settings.heads_repo  # TODO

    def build(self) -> None:
        # TODO: share this consul code
        consul = "http://consul.service.consul:8500"

        host = self.ctx.host
        service = self.name

        resp = requests.put(
            url=f"{consul}/v1/kv/buildbot/instances/{host}/{service}",
            data="",
        )

        assert resp.status_code == 200, f"{resp.status_code} {resp.text}"

    def get_archive(self, kind: str) -> None:
        cmd = f"get_{kind}_archive"
        machine = self.info['machine']
        pkg, arch = packages.latest_semver(self.name, machine)

        self.runner.run_remote_rpc(cmd, params=dict(
            app_name=pkg['name'],
            url=arch['url'],
            digest=arch['digest'],
        ), user="build")

    def get_zip_archive(self) -> None:
        return self.get_archive("zip")

    def get_tar_archive(self) -> None:
        return self.get_archive("tar")

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
        return settings.ports[self.name]

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

        self.register_service_with_consul(self.name, self.port)

    def execute(self) -> List[Dict[str, Any]]:
        adduser(self.runner, self.user, self.extra_groups())

        self.setup()

        systemd_args = self.systemd_args()
        if systemd_args is not None:
            rendered = systemd(**systemd_args)
            rendered["mode"] = 0o644
            self.runner.run_remote_rpc("systemd", params=rendered)

        self.register_for_monitoring()
        self.register_service()
        self.setup_sudo_for_build_restart()  # TODO: only needed for code we build from git

        return self.runner.execute()

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

    def register_for_monitoring(self) -> None:
        port = self.metrics_port

        if port is None:
            return

        host = self.ctx.record['host']

        filename = f"{self.name}.yml"

        target = f"{host}.node.consul:{port}"
        labels = {
            "job": self.name,
            "host": self.ctx.host,
        }

        metrics_path = self.metrics_path()
        if metrics_path is not None:
            labels["__metrics_path__"] = metrics_path

        for k, v in sorted(self.metrics_params().items()):
            labels[f"__param_{k}"] = v

        static_config = {
            "targets": [target],
            "labels": labels
        }

        cfg = [static_config]

        content = yaml.dump(cfg, default_flow_style=False)

        consul = "http://consul.service.consul:8500"

        # TODO: only write if different. Maybe it already handles this for us

        resp = requests.put(
            url=f"{consul}/v1/kv/prometheus/by-host/{host}/{filename}",
            data=content,
        )

        assert resp.status_code == 200, f"{resp.status_code} {resp.text}"

    def service_level_monitoring(self):
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

        consul = "http://consul.service.consul:8500"

        resp = requests.put(
            url=f"{consul}/v1/kv/prometheus/by-service/{filename}",
            data=content,
        )

        assert resp.status_code == 200, f"{resp.status_code} {resp.text}"
