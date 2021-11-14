from typing import Dict

import provision.hashicorp_vault as hashicorp_vault

from .service import Service


class Rtunneld(Service):
    name = "rtunneld"
    description = "reverse ssh tunnel manager"
    deps = ["consul"]

    # def extra_groups(self) -> List[str]:
    #     return super().extra_groups() + ["i2c", "gpio", "audio"]
    #
    def env(self) -> Dict[str, str]:
        return self.ctx.record.env['rtunneld']

    def command_line(self) -> str:
        return self.exe()

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
