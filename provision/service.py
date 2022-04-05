import copy
import json
import os
from typing import List, Dict, Optional, Any, Tuple

import provision.packages as packages

from .context import Context
from .run_remote_script import Runner
from .service_util import adduser, template
from .systemd import ServiceConfig, systemd


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

    def get_archive(self, kind: str, pkg_name: Optional[str] = None) -> None:
        cmd = f"get_{kind}_archive"
        machine = self.info['machine']
        pkg_name = pkg_name or self.name

        arch = {
            "armv7l": "armhf",
            "aarch64": "arm64",
            "armv6l": "armv6",
        }[machine]

        pkgs = []
        with open(f"checksums") as fp:
            for a in fp:
                if len(a.strip()) == 0:
                    continue  # skip empty lines
                digest, filename = a.split()
                pkg = packages.Package.parse(filename)

                if pkg.name.replace("_", "-") != pkg_name.replace("_", "-"):
                    continue

                pkg.digest = digest
                pkgs.append(pkg)

        pkgs = [p for p in pkgs if p.arch == arch]

        pkg: packages.Package = max(pkgs, key=lambda p: p.version)

        self.runner.run_remote_rpc(cmd, params=dict(
            app_name=pkg_name,
            url=f"file:///home/static/builds/{pkg.filename}",
            digest=pkg.digest,
        ), user="build")

    def get_zip_archive(self) -> None:
        return self.get_archive("zip")

    def get_tar_archive(self, **kw) -> None:
        return self.get_archive("tar", **kw)

    def get_tar_bz_archive(self) -> None:
        return self.get_archive("tar_bz")

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

    def ensure_line_in_file(self, path: str, line: str):
        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename=path,
            line=line,
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

    def enable_i2c(self):
        # TODO: maybe this should be in a library and not attached to Service
        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="dtparam=i2c_arm=on",
        ))

        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/etc/modules",
            line="i2c-dev",
        ))


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

    def instance_name(self) -> str:
        return ""

    def execute(self) -> List[Dict[str, Any]]:
        adduser(self.ctx, self.runner, self.user, self.extra_groups())

        self.setup()

        args = self.systemd_args()
        self.systemd_new(args)

        self.register_serf_tags()
        self.setup_sudo_for_build_restart()  # TODO: only needed for code we build from git

        return self.runner.execute()

    def systemd_new(self, cfg: ServiceConfig):
        c = copy.deepcopy(cfg)
        c.name = c.name or self.name
        c.user = c.user or self.user
        c.group = c.group or self.group  # TODO: or self.name?
        c.description = c.description or self.description
        c.working_dir = c.working_dir or self.working_dir()
        c.env = c.env | self.ctx.record.env.get(self.name, {})
        params = systemd(c)
        params["mode"] = 0o644
        self.runner.run_remote_rpc("systemd", params=params)

    def systemd_args(self) -> ServiceConfig:
        raise NotImplementedError

    @property
    def metrics_port(self) -> Optional[int]:
        return self.port

    def register_serf_tags(self) -> None:
        service_tags = []

        if self.port is not None:
            service_tags.append(f"sp:{self.port}")

        instance_name = self.instance_name()
        if instance_name:
            service_tags.append(f"i:{instance_name}")

        cfg = {
            "tags": {
                f"s:{self.name}": " ".join(service_tags)
            }
        }

        self.ensure_file(
            path=self.home_for_user("serf", "serf-cfg", f"service-{self.name}.json"),
            mode=0o640,
            user="serf",
            group="serf",
            content=json.dumps(cfg, indent=4)
        )

        self.runner.run_remote_rpc("systemctl_restart_if_running", params=dict(service_name="serf"))
