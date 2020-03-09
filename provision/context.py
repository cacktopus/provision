from dataclasses import dataclass
from typing import Dict, Set, Any

from .info import Info


@dataclass
class Context:
    root_conn: Info
    record: Dict[str, Any]
    tags: Set[str]
    host: str
