from typing import Any, Optional

from fabric import Connection  # type: ignore


class Info:
    def __init__(self, c: Connection):
        self._c = c

    def new_connection_as(self, username: str, forward_agent: Optional[bool] = None, **kw: Any) -> 'Info':
        return Info(Connection(
            self._c.host,
            user=username,
            port=self._c.port,
            gateway=self._c.gateway,
            forward_agent=forward_agent,
            **kw,
        ))

    @property
    def host(self) -> str:
        result: str = self._c.host
        return result

    def current_user(self) -> str:
        result: str = self._c.user
        return result

    def put(self, local: str, remote: str) -> None:
        print("put [*]: {} {}".format(local, remote))
        self._c.put(local=local, remote=remote)
