import os
import re
from dataclasses import dataclass
from typing import Tuple


class PkgNotFound(RuntimeError):
    pass


arch_map = {
    "armv6l": "arm6",
    "armv7l": "arm7",
}

re_pkg = re.compile(r'(.*)[_-]?(\d+)\.(\d+)\.(\d+)')


@dataclass
class Package:
    name: str
    arch: str
    major: int
    minor: int
    patch: int
    digest: str = ""
    orig: str = ""

    @property
    def version(self) -> Tuple[int, int, int]:
        return self.major, self.minor, self.patch

    @property
    def filename(self) -> str:
        if self.orig:
            return self.orig
        return f"{self.name}_{self.major}.{self.minor}.{self.patch}_{self.arch}.tar.gz"

    @staticmethod
    def parse(f: str):
        parts = os.path.basename(f).split(".")

        gz = parts.pop()
        assert gz in ("gz", "bz2")

        tar = parts.pop()
        assert tar == "tar"

        b = ".".join(parts)

        ma = re_pkg.search(f)
        assert ma

        name = ma.group(1)

        for opt in ["arm64", "amd64", "armhf", "armv7", "armv6l", "armv6"]:
            if opt in f:
                arch = opt
                break
        else:
            raise Exception("unknown arch")

        arch = {
            "armv7": "armhf",
            "armv6l": "armhf",
        }.get(arch, arch)

        ma, mi, pa = [int(p) for p in [ma.group(2), ma.group(3), ma.group(4)]]
        return Package(name=name, arch=arch, major=ma, minor=mi, patch=pa, orig=f)
