from dataclasses import dataclass
from typing import Set

from .info import Info
from .settings import Settings, Host


@dataclass
class Context:
    root_conn: Info
    record: Host
    tags: Set[str]
    host: str
    settings: Settings
