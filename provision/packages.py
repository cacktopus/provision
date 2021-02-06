import os
from dataclasses import dataclass
from typing import Tuple, Dict, Any

import yaml

_packages = yaml.load(open('packages.yaml'))


class PkgNotFound(RuntimeError):
    pass


arch_map = {
    "armv6l": "arm6",
    "armv7l": "arm7",
}


@dataclass
class Package:
    name: str
    arch: str
    major: int
    minor: int
    patch: int
    digest: str = ""

    @property
    def version(self) -> tuple[int, int, int]:
        return self.major, self.minor, self.patch

    @property
    def filename(self) -> str:
        return f"{self.name}_{self.major}.{self.minor}.{self.patch}_{self.arch}.tar.gz"

    @staticmethod
    def parse(f: str):
        parts = os.path.basename(f).split(".")

        gz = parts.pop()
        assert gz == "gz"

        tar = parts.pop()
        assert tar == "tar"

        b = ".".join(parts)

        name, version, arch = b.split("_")

        ma, mi, pa = [int(p) for p in version.split(".")]
        return Package(name=name, arch=arch, major=ma, minor=mi, patch=pa)


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
