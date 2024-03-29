from typing import Dict

from .service import Provision


class Firewall(Provision):
    name = "firewall"
    deps = ["service-ready"]

    def template_vars(self) -> Dict[str, str]:
        return {"network": self.ctx.settings.network}

    def setup(self) -> None:
        self.template(
            name="firewall-setup.sh",
            location="/usr/local/sbin/firewall-setup.sh",
            user="root",
            group="root",
            mode=0o744,
            vars={
                "network": self.ctx.record.primary_interface,
                "allow": self.ctx.record.firewall.allow,
                "block": self.ctx.record.firewall.block,
            },
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
