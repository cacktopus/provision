import json

import provision.hashicorp_vault as hashicorp_vault

from .service import Service
from .systemd import ServiceConfig


class Rtunneld(Service):
    name = "rtunneld"
    deps = ["service-ready"]

    def setup(self) -> None:
        self.get_tar_archive()

        vault_client = hashicorp_vault.Client()
        secret = vault_client.get("ssh/tunnel")
        rsa: str = secret['id_rsa']

        # TODO: move this out of .ssh
        remote_file = self.user_home(".ssh", 'tunnel.id_rsa')

        # TODO: just check checksums before sending contents of sensitive files
        self.ensure_file(
            path=remote_file,
            mode=0o400,
            user=self.user,
            group=self.group,
            content=rsa,
        )

        cfg = self.ctx.record.rtunneld.to_json() if self.ctx.record.rtunneld else {}

        self.ensure_file(
            path=self.user_home("etc", "rtunneld.yml"),
            mode=0o640,
            user=self.user,
            group=self.group,
            content=json.dumps(cfg, indent=4),
        )

    def systemd_args(self) -> ServiceConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="reverse ssh tunnel manager",
            type="simple",  # TODO: notify?
            after=["network.target"],
            env={
                "CONFIG_FILE": self.user_home("etc", "rtunneld.yml")
            }
        )
