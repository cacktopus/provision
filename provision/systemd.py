from typing import Dict, List, Any, Optional, Tuple

import attr


@attr.s(auto_attribs=True)
class BaseConfig:
    exec_start: str
    description: str

    type: str = ""
    name: str = ""
    user: str = ""
    group: str = ""

    working_dir: str = ""
    exec_reload: str = ""
    exec_start_pre: str = ""
    default_dependencies: str = ""

    restart: str = ""
    restart_sec: str = ""
    remain_after_exit: str = ""

    env: Dict[str, str] = attr.Factory(dict)
    capabilities: List[str] = attr.Factory(list)
    after: List[str] = attr.Factory(list)
    before: List[str] = attr.Factory(list)
    wanted_by: List[str] = attr.Factory(list)

    def build_config(self) -> Dict[str, Any]:
        env = [f"Environment={k}={v}" for k, v in sorted(self.env.items())]

        service_content = config(
            section(
                "Unit",
                item("Description", self.description),
                many("After", self.after),
                many("Before", self.before),
                item("DefaultDependencies", self.default_dependencies),
            ),

            section(
                "Service",
                item("Type", self.type),
                item("User", self.user),
                item("Group", self.group),
                item("WorkingDirectory", self.working_dir),
                item("Restart", self.restart),
                item("RestartSec", self.restart_sec),
                item("RemainAfterExit", self.remain_after_exit),
                many("AmbientCapabilities", self.capabilities),
                item("ExecStart", self.exec_start),
                item("ExecStartPre", self.exec_start_pre),
                item("ExecReload", self.exec_reload),
                *env,
            ),

            section(
                "Install",
                many("WantedBy", self.wanted_by),
            ),
        )

        return dict(
            service_name=self.name,
            service_filename=f"/etc/systemd/system/{self.name}.service",
            service_content=service_content,
            mode=0o644,
        )


@attr.s(auto_attribs=True)
class ServiceConfig(BaseConfig):
    type: str = "simple"
    restart: str = "always"
    restart_sec: str = "15"
    remain_after_exit: str = "no"
    after: List[str] = attr.Factory(lambda: ["network.target"])
    wanted_by: List[str] = attr.Factory(lambda: ["multi-user.target"])


@attr.s(auto_attribs=True)
class OneshotConfig(BaseConfig):
    type: str = "oneshot"


def section(name: str, *items: Optional[str]) -> Tuple[str, List[str]]:
    return name, [i for i in items if i is not None]


def config(*sections: section) -> str:
    result = []
    for name, items in sections:
        result.append(f"[{name}]")
        for item in items:
            result.append(item)
        result.append("")
    return "\n".join(result)


def item(key: str, val: str) -> Optional[str]:
    if val:
        return f"{key}={val}"
    return None


def many(key: str, vals: List[str]) -> Optional[str]:
    if len(vals) > 0:
        val = " ".join(vals)
        return f"{key}={val}"
    return None
