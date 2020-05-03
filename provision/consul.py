from typing import List, Dict, Any

from jinja2 import Template

from .service import Service
from .settings import inventory, settings


class Consul(Service):
    name = "consul"
    user = "consul"
    group = "consul"
    description = "service discovery"
    deps = ["consul-bootstrap", "packages2"]

    def reload(self) -> str:
        return f"{self.exe()} reload"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["systemd-journal"]

    def capabilities(self) -> List[str]:
        return ["CAP_NET_BIND_SERVICE"]

    def command_line(self) -> str:
        return f"{self.exe()} agent -config-dir consul.d --dns-port 53"

    def metrics_path(self) -> str:
        return "/v1/agent/metrics"

    def metrics_params(self) -> Dict[str, str]:
        return {"format": "prometheus"}

    def template_vars(self) -> Dict[str, str]:
        kind = self.ctx.record.get("consul", "client")
        assert kind in ("server", "client")

        server = kind == "server"

        network = settings['network']

        lookup = r'"{{ GetPrivateInterfaces | include \"network\" \"%s\" | attr \"address\" }}"' % network
        bind_addr = f'"{self.ctx.record["consul_ip"]}"' if server else lookup

        client_addr = '"0.0.0.0"'

        hostname: str = self.ctx.record['host']
        return dict(
            hostname=hostname,
            bind_addr=bind_addr,
            client_addr=client_addr,
            server="true" if server else "false",
            retry_join=retry_join(),
            bootstrap="bootstrap_expect = 3" if server else ""
        )

    def setup(self) -> None:
        self.get_zip_archive()

        self.runner.run_remote_rpc("ensure_link", user=self.user, params=dict(
            src=self.exe(),
            dst=self.user_home("bin", "consul"),
        ))

        self.ensure_dir(
            path=self.user_home("consul.d"),
            mode=0o750,
            user=self.user,
            group=self.group,
        )

        self.template(
            name="consul.d/config.hcl",
            location=self.user_home("consul.d/config.hcl"),
            user=self.user,
            group=self.group,
        )

        self.runner.run_remote_rpc("systemctl_disable", params=dict(
            service_name="systemd-resolved"
        ))

    def consul_health_checks(self) -> List[Dict[str, Any]]:
        return []

    def register_service(self) -> None:
        self.register_service_with_consul("consul-fe", 8500, tags=["frontend"])

    def reload_consul(self) -> None:
        pass


class ConsulBootstrap(Consul):
    port = None
    action_name = "consul-bootstrap"
    deps = ["setup-host", "user(build)"]

    def register_service(self) -> None:
        pass


def retry_join() -> str:
    consul_hosts = [
        r for r
        in inventory
        if r.get('consul', 'client') == 'server' and ("consul" in r['tags'] or "consul-bootstrap" in r['tags'])
    ]

    num_hosts = len(consul_hosts)
    assert num_hosts >= 3, f"Need at least 3 consul hosts, found {num_hosts}"

    return ", ".join('"{}"'.format(r['consul_ip']) for r in consul_hosts)


def indent(spaces: int, s: str) -> str:
    lines = s.splitlines(keepends=True)
    result = "".join(" " * spaces + line for line in lines)
    return result


def check_redis(host: str, port: int) -> str:
    assert host.endswith(".node.consul")
    t = Template(open("templates/consul.d/{}".format("check_redis")).read())
    content = t.render(hostport="{}:{}".format(host, port))
    return indent(4, content)


def check_tcp(service_name: str, host: str, port: int) -> str:
    assert host.endswith(".node.consul")
    t = Template(open("templates/consul.d/{}".format("check_tcp_connection")).read())
    content = t.render(
        id=service_name + "_tcp_connection",
        name="tcp connection to " + service_name,
        host=host,
        port=port,
    )
    return indent(4, content)


def check_http(service_name: str, url: str, method: str = "GET") -> str:
    assert url.startswith("http://")
    assert ".node.consul" in url
    t = Template(open("templates/consul.d/{}".format("check_http_endpoint")).read())
    content = t.render(
        id=service_name + "_http_endpoint",
        name="http health check for " + service_name,
        url=url,
        method=method,
    )
    return indent(4, content)


def lock(name: str, *cmd: str) -> str:
    return "/home/build/builds/consul/prod/consul lock -child-exit-code {} {}".format(
        name,
        " ".join(cmd),
    )
