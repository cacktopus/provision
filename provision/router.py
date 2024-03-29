from provision import hashicorp_vault

from .service import Provision
from .systemd import OneshotConfig


class Router(Provision):
    name = "router"
    deps = ["service-ready"]

    def setup(self) -> None:
        cfg = self.ctx.settings.router

        vault_client = hashicorp_vault.Client()
        wpa_passphrase = vault_client.get(cfg.vault_wpa_passphrase_key)["wpa_passphrase"]

        self.template(
            name="hostapd.conf",
            location="/etc/hostapd/hostapd.conf",
            user="root",
            group="root",
            mode=0o600,
            vars=dict(
                interface=cfg.interface,
                ssid=cfg.ssid,
                wpa_passphrase=wpa_passphrase,
            )
        )

        self.template(
            name="dhcpcd.conf",
            location="/etc/dhcpcd.conf",
            user="root",
            group="root",
            mode=0o664,
            vars=dict(
                interface=cfg.interface,
                ip_address=f"{cfg.ip_address}/{cfg.netmask}",
            )
        )

        self.template(
            name="dnsmasq.conf",
            location="/etc/dnsmasq.d/dnsmasq.conf",
            user="root",
            group="root",
            mode=0o644,
            vars=dict(
                dhcp_range=cfg.dhcp_range,
                hostname=self.ctx.record.host,
                domain=cfg.domain,
                interface=cfg.interface,
                ip_address=cfg.ip_address,
            )
        )

        self.ensure_file(
            path="/etc/sysctl.d/routed-ap.conf",
            mode=0o644,
            user="root",
            group="root",
            content="net.ipv4.ip_forward=1\n"
        )

        # TODO: put in firewall setup?
        params = OneshotConfig(
            name="iptables-masquerade",
            description="iptables-masquerade",
            exec_start=f"/usr/sbin/iptables -t nat -A POSTROUTING -o {cfg.upstream_interface} -j MASQUERADE",
            remain_after_exit="yes",
            before=["network.target"],
            wanted_by=["network.target"],
        ).build_config()

        self.runner.run_remote_rpc("systemd", params=params)
        self.runner.run_remote_rpc("systemctl_unmask", params=dict(service_name="hostapd"))
        self.runner.run_remote_rpc("systemctl_enable", params=dict(service_name="hostapd", now=True))
