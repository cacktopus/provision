from typing import Optional, Dict, List, Union

from .service_util import template


def systemd(
        service_name: str,
        user: str,
        description: str,
        exec_start: str,
        working_dir: str,
        group: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        capabilities: Optional[List[str]] = None,
        reload: Optional[str] = None,
        start_after: Optional[str] = None,
        extra: Optional[Dict[str, str]] = None,
) -> Dict[str, Union[str, int]]:
    group = group or user
    env = env or {}
    capabilities = capabilities or []

    filename = service_name

    env_str = "\n".join(f"Environment={k}={v}" for k, v in sorted(env.items()))
    capabilities_str = "\n".join(f"AmbientCapabilities={cap}" for cap in capabilities)

    reload = f"ExecReload={reload}" if reload is not None else ""
    after = f"After={start_after}" if start_after else ""

    extra = "\n".join(f"{k}={v}" for k, v in extra.items()) if extra is not None else ""

    service_content = template(
        "systemd",
        vars={
            "after": after,
            "description": description,
            "exec_start": exec_start,
            "user": user,
            "group": group,
            "working_dir": working_dir,
            "env": env_str,
            "capabilities": capabilities_str,
            "reload": reload,
            "extra": extra,
        },
    )

    return dict(
        service_name=service_name,
        service_filename=f"/etc/systemd/system/{filename}.service",
        service_content=service_content,
    )
