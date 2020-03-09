from typing import Tuple, Dict, Any

import yaml

_packages = yaml.load(open('packages.yaml'))


class PkgNotFound(RuntimeError):
    pass


arch_map = {
    "armv6l": "arm6",
    "armv7l": "arm7",
}


def find(name: str, version: str, arch: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    arch = arch_map.get(arch, arch)
    for pkg in _packages:
        if pkg['name'] == name and pkg['version'] == version:
            return pkg, pkg['arch'][arch]

    raise PkgNotFound


def latest_semver(name: str, arch: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    arch = arch_map.get(arch, arch)
    options = []
    for pkg in _packages:
        if pkg['name'] != name:
            continue
        parts = [int(p) for p in pkg['version'].strip().split(".")]
        options.append((parts, pkg))
    _, pkg = max(options)
    return pkg, pkg['arch'][arch]
