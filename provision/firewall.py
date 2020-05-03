from typing import Dict

from .service import Provision
from .settings import settings


class Firewall(Provision):
    name = "firewall"
    deps = ["service-ready", "taglist"]

    def template_vars(self) -> Dict[str, str]:
        return {"network": settings['network']}

    def setup(self) -> None:
        self.template(
            name="firewall-setup.sh",
            location="/usr/local/sbin/firewall-setup.sh",
            user="root",
            group="root",
            mode=0o744,
        )

        service_name = "firewall.service"
        self.template(
            name=service_name,
            location=f"/etc/systemd/system/{service_name}",
            user="root",
            group="root",
            mode=0o644,
        )

        # TODO: only enable if provisioning for the first time
        self.runner.run_remote_rpc("systemctl_enable", params=dict(service_name=service_name))
        self.runner.run_remote_rpc("systemctl_restart_if_running", params=dict(service_name=service_name))
