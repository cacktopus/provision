import attr
from provision import hashicorp_vault

from .service import Provision
from .systemd import systemd_new, ServiceConfig


@attr.s(auto_attribs=True)
class RouterConfig:
    interface: str
    ssid: str
    wpa_passphrase: str
    ip_address: str
    netmask: int
    dhcp_range: str
    upstream_interface: str


class Router(Provision):
    name = "router"
    deps = ["service-ready"]

    def setup(self) -> None:
        vault_client = hashicorp_vault.Client()
        wpa_passphrase = vault_client.get(f"wifi/theheads")["wpa_passphrase"]

        cfg = RouterConfig(
            interface="wlan0",
            ssid="theheads2",
            wpa_passphrase=wpa_passphrase,
            ip_address="192.168.4.1",
            netmask=24,
            dhcp_range="192.168.4.2,192.168.4.99,255.255.255.0,24h",
            upstream_interface="eth0",
        )

        package_list = [
            "hostapd",
            "dnsmasq",
            "netfilter-persistent",
            "iptables-persistent",
        ]

        self.template(
            name="hostapd.conf",
            location="/etc/hostapd/hostapd.conf",
            user="root",
            group="root",
            mode=0o600,
            vars=dict(
                interface=cfg.interface,
                ssid=cfg.ssid,
                wpa_passphrase=cfg.wpa_passphrase,
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
                interface=cfg.interface,
                dhcp_range=cfg.dhcp_range,
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

        params = systemd_new(ServiceConfig(
            name="iptables-masquerade",
            exec_start=f"/usr/sbin/iptables -t nat -A POSTROUTING -o {cfg.upstream_interface} -j MASQUERADE",
            type="oneshot",
            remain_after_exit="yes",
            before=["network.target"],
        ))
        self.runner.run_remote_rpc("systemd", params=params)

        self.runner.run_remote_rpc("install_packages", params=dict(packages=package_list))

        self.runner.run_remote_rpc("systemctl_unmask", params=dict(service_name="hostapd"))
        self.runner.run_remote_rpc("systemctl_enable", params=dict(service_name="hostapd", now=True))
