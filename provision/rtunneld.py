import provision.hashicorp_vault as hashicorp_vault
from .service import Service


class Rtunneld(Service):
    name = "rtunneld"
    description = "reverse ssh tunnel manager"
    deps = ["service-ready"]
    repo = "rtunneld"

    def command_line(self) -> str:
        return self.exe()

    def setup(self) -> None:
        vault_client = hashicorp_vault.Client()
        secret = vault_client.get("ssh/tunnel")
        rsa: str = secret['id_rsa']

        self.build()

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
