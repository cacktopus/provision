from provision import hashicorp_vault

from .service import Provision


class Router(Provision):
    name = "router"
    deps = ["service-ready"]

    def setup(self) -> None:
        package_list = [
            "hostapd",
            "dnsmasq",
            "netfilter-persistent",
            "iptables-persistent",
        ]

        vault_client = hashicorp_vault.Client()
        wifi = vault_client.get(f"wifi/theheads")

        self.template(
            name="hostapd.conf",
            location="/etc/hostapd/hostapd.conf",
            user="root",
            group="root",
            vars=dict(
                interface="wlan1",
                ssid="theheads2",
                wpa_passphrase=wifi["wpa_passphrase"],
            )
        )

        self.runner.run_remote_rpc("install_packages", params=dict(packages=package_list))

        self.runner.run_remote_rpc("systemctl_unmask", params=dict(service_name="hostapd"))
        self.runner.run_remote_rpc("systemctl_enable", params=dict(service_name="hostapd", now=True))
