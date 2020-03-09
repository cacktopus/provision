from collections import OrderedDict
from typing import Callable, List, Optional, Dict

import networkx as nx  # type: ignore

from .context import Context

actions: Dict[str, Callable[[Context], None]] = OrderedDict()
G = nx.DiGraph()


class Action:
    def __init__(self, name: Optional[str] = None, deps: Optional[List[str]] = None) -> None:
        # TODO: handle the no argument case
        self.name = name
        self.deps = deps or []

    def __call__(self, func: Callable[[Context], None]) -> None:
        target = self.name or func.__name__

        for dep in self.deps:
            assert "_" not in target, target
            assert "_" not in dep, dep
            G.add_edge(dep, target)

        assert target not in actions, f"duplicate action {target}"
        # print(f"registering {target}")
        actions[target] = func


def add_dep(target: str, *deps: str) -> None:
    for dep in deps:
        assert "_" not in target, target
        assert "_" not in dep, dep
        G.add_edge(dep, target)
