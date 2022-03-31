from typing import Dict, Any

import yaml

from .service import Service

from .hashicorp_vault import Client


class Alertmanager(Service):
    name = "alertmanager"
    description = "Alert Manager"
    deps = ["serf"]

    def template_vars(self) -> Dict[str, str]:
        vault_client = Client()

        email = vault_client.get("alertmanager/email")  # TODO: allow a 404 on this
        slack = vault_client.get("alertmanager/slack")  # TODO: allow a 404 on this

        receiver: Dict[str, Any] = {
            "name": "email-me"
        }

        if email is not None:
            receiver['email_configs'] = [{
                "to": email['address'],
                "from": email['address'],
                "smarthost": "smtp.gmail.com:587",
                "auth_username": email['address'],
                "auth_identity": email['address'],
                "auth_password": email['password'],
            }]

        if slack is not None:
            slack_api_url = f"slack_api_url: {slack['url']}"
            receiver['slack_configs'] = [{
                "api_url": slack['url'],
                "channel": '"#alerts"',
            }]
        else:
            slack_api_url = ""

        return dict(
            slack_api_url=slack_api_url,
            receivers=yaml.dump([receiver], default_flow_style=False)
        )

    def command_line(self) -> str:
        initial_peers = " ".join(
            f"--cluster.peer {peer}"
            for peer in self.ctx.settings.get_hosts("alertmanager", port=9094)  # 9094 used for cluster communication
        )

        config = self.user_home("etc", "alertmanager.yml")
        storage = self.user_home("etc", "alertmanager_data")

        return f"{self.exe()} --config.file {config} --storage.path {storage} {initial_peers}"

    def setup(self) -> None:
        self.get_tar_archive()

        self.template(
            name="alertmanager.yml",
            location=self.user_home("etc", "alertmanager.yml"),
            user=self.user,
            group=self.group,
            mode=0o644,
        )
