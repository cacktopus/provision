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

        self.runner.run_remote_rpc("install_packages", params=dict(packages=package_list))
