from typing import Dict, List

import attr

from .service_util import template


@attr.s(auto_attribs=True)
class ServiceConfig:
    exec_start: str

    name: str = ""
    user: str = ""
    group: str = ""

    type: str = "simple"
    description: str = ""
    working_dir: str = ""
    exec_reload: str = ""
    exec_start_pre: str = ""

    restart: str = "always"
    restart_sec: int = 15
    remain_after_exit: str = "no"

    env: Dict[str, str] = attr.Factory(dict)
    capabilities: List[str] = attr.Factory(list)
    after: List[str] = attr.Factory(list)
    before: List[str] = attr.Factory(list)
    wanted_by: List[str] = attr.Factory(lambda: ["multi-user.target"])


def systemd(cfg: ServiceConfig, mode: int = 0o644):
    tmpl_vars = attr.asdict(cfg)
    tmpl_vars["capabilities"] = " ".join(cfg.capabilities)
    tmpl_vars["after"] = " ".join(cfg.after)
    tmpl_vars["before"] = " ".join(cfg.before)
    tmpl_vars["wanted_by"] = " ".join(cfg.wanted_by)
    tmpl_vars["env"] = "\n".join(f"Environment={k}={v}" for k, v in sorted(cfg.env.items()))

    if cfg.type == "oneshot":
        del tmpl_vars["restart"]
        del tmpl_vars["restart_sec"]

    service_content = template("systemd_new", vars=tmpl_vars)

    return dict(
        service_name=cfg.name,
        service_filename=f"/etc/systemd/system/{cfg.name}.service",
        service_content=service_content,
        mode=mode,
    )
