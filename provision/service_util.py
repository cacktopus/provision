from typing import List, Dict, Optional, Any, Tuple

from jinja2 import Template

import provision.hashicorp_vault as hashicorp_vault
from .settings import mainuser, jsu
from .run_remote_script import Runner


# TODO: move this?
def template(
        name: str,
        fix_line_endings: Optional[bool] = True,
        vars: Optional[Dict[str, Any]] = None,
        template_delimiters: Optional[Tuple[str, str]] = None
) -> str:
    if template_delimiters:
        bgn, end = template_delimiters
        kwargs = dict(variable_start_string=bgn, variable_end_string=end)
    else:
        kwargs = {}

    vars = vars or {}
    assert isinstance(vars, dict)
    t = Template(open("templates/{}".format(name)).read(), **kwargs)  # type: ignore
    content = t.render(**vars, )

    if fix_line_endings:
        if not content.endswith("\n"):
            content += "\n"

    return content


# TODO! move this
def adduser(
        runner: Runner,
        user: str,
        groups: Optional[List[str]] = None
) -> None:
    groups = groups or []
    vault_client = hashicorp_vault.Client()

    authorized_keys = []
    for u in {mainuser, jsu}:
        ssh = vault_client.get(f"ssh/{u}")
        pub_key: str = ssh['id_rsa.pub']
        authorized_keys.append(pub_key)

    runner.run_remote_rpc("new_user_setup", params={
        "user": user,
        "authorized_keys": authorized_keys,
        "groups": groups,
    })

    known_hosts = list(vault_client.get("known_hosts").values())

    runner.run_remote_rpc("phase_2_setup", params={
        "known_hosts": known_hosts,
        "aliases": template("alias"),
        "ssh_config": template("ssh_config"),
    }, user=user)
