import attr
import yaml
from typing import List, Dict, Set, Optional

_ports: Dict[str, int] = yaml.load(open('ports.yaml'), Loader=yaml.FullLoader)


@attr.s(auto_attribs=True)
class Host:
    host: str
    sudo: str
    role: str
    primary_interface: str

    initial_ip: str = ""
    initial_password: str = ""

    tags: List[str] = attr.Factory(list)
    kv: Dict[str, str] = attr.Factory(dict)
    env: Dict[str, Dict[str, str]] = attr.Factory(dict)


@attr.s(auto_attribs=True)
class Repo:
    name: str
    url: str
    default_commit: str


@attr.s(auto_attribs=True)
class Serf:
    port: int
    cluster_name: str


@attr.s(auto_attribs=True)
class Router:
    interface: str
    ssid: str
    ip_address: str
    netmask: int
    dhcp_range: str
    upstream_interface: str
    vault_wpa_passphrase_key: str


@attr.s(auto_attribs=True)
class Settings:
    mainuser: str
    network: str
    serf: Serf
    build_storage_url: str
    static_files_path: str

    router: Optional[Router]

    repos: List[Repo]

    env: Dict[str, Dict[str, str]] = attr.Factory(dict)
    whitelist_hosts: List[str] = attr.Factory(list)

    whitelist_tags: List[str] = attr.Factory(list)
    blacklist_tags: List[str] = attr.Factory(list)
    start_at: str = ""

    common_tags: List[str] = attr.Factory(list)

    inventory: List[Host] = attr.Factory(list)

    deploy_gateway: str = ""

    def get_repo_by_name(self, name) -> Repo:
        result = [r for r in self.repos if r.name == name]
        if len(result) != 1:
            raise AttributeError(f"Problem finding repo ({name})")
        return result[0]

    @property
    def all_tags(self) -> Set[str]:
        tags = set(self.common_tags)
        for host in self.inventory:
            tags |= set(host.tags)
        return tags

    def get_host_names_by_tag(self, tag: str) -> List[str]:
        return [
            h.host
            for h in self.inventory
            if tag in h.tags or tag in self.common_tags
        ]

    def get_hosts(self, *tags: str, port: Optional[int] = None) -> List[str]:
        if port is None:
            port = _ports[tags[0]]

        host_names: Set[str] = set()
        for tag in tags:
            host_names |= set(self.get_host_names_by_tag(tag))

        hosts = [self.by_name[h] for h in host_names]
        result = sorted(f"{h.host}.local:{port}" for h in hosts)

        return result

    @property
    def by_name(self) -> Dict[str, Host]:
        return {h.host: h for h in self.inventory}

    @property
    def ports(self) -> Dict[str, int]:
        return _ports
