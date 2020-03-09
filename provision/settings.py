import sys
from typing import List, Dict, Any, Set, Optional

import yaml

settings_file = sys.argv[1]  # TODO: terrible

settings: Dict[str, Any] = yaml.load(open(settings_file), Loader=yaml.FullLoader)
ports: Dict[str, int] = yaml.load(open('ports.yaml'), Loader=yaml.FullLoader)
inventory = settings['inventory']
by_mac = {h['mac']: h for h in inventory if h.get('mac') is not None}
by_host = {h['host']: h for h in inventory}


def get_host_names_by_tag(tag: str) -> List[str]:
    return [
        record['host']
        for record in inventory
        if tag in record['tags'] or tag in settings['common_tags']
    ]


def all_tags() -> Set[str]:
    tags = set(settings['common_tags'])
    for record in inventory:
        tags |= set(record['tags'])
    return tags


mainuser = settings['mainuser']
jsu = 'jsu'  # TODO
versions = settings['versions']
env = settings['env']

git_build = settings['git']['build']

heads_repo = f"{git_build}/heads.git"


def get_hosts(*tags: str, port: Optional[int] = None) -> List[str]:
    if port is None:
        port = ports[tags[0]]
    hosts: Set[str] = set()
    for tag in tags:
        hosts |= set(get_host_names_by_tag(tag))

    records = [by_host[h] for h in hosts]
    result = sorted(f"{r['host']}.node.consul:{port}" for r in records)

    return result
