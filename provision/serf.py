from .service import Service


class Serf(Service):
    name = "serf"
    description = "hashicorp serf"
    deps = ["consul"]
    port = None

    def command_line(self) -> str:
        join_hosts = [
            f"-retry-join {host}.local"
            for host in
            self.ctx.settings.get_host_names_by_tag("serf")
        ]

        return " ".join([
            self.exe(),
            "agent",
            # "-discover", self.ctx.settings.serf.cluster_name,
            # "-snapshot", self.etc("serf.snapshot"),
            "-bind", f"0.0.0.0:{self.ctx.settings.serf.port}",
            "-tag", f"cluster={self.ctx.settings.serf.cluster_name}",
            "-tag", f"role={self.ctx.record.role}",
            "-iface", self.ctx.record.primary_interface,
            *join_hosts,
        ])

    def setup(self) -> None:
        self.get_tar_archive()

    def register_mdns(self) -> None:
        pass
