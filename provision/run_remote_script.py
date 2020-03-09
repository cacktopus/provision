import io
import pickle
import time
import zipapp
from base64 import b64encode, b64decode
from typing import Dict, Any, List, Optional, Mapping, Set

from .info import Info

LIB_NAME = "remote_scripts.pyz"


class Runner:
    def __init__(self, conn: Info, sudo: Optional[bool] = True):
        self.conn = conn
        self.steps: List[Any] = []
        self.done = False
        self.sudo = sudo

    def run_remote_rpc(
            self,
            method: str,
            params: Mapping[str, Any],
            user: Optional[str] = None,
    ) -> None:
        rpc = self._append_remote_script(user=user, rpc_payload=dict(
            method=method,
            params=params,
            user=user,
        ))
        self.steps.append(rpc)

    _upload_cache: Set[str] = set()

    @classmethod
    def _upload_zip(cls, conn: Info) -> None:
        host = conn.host
        if host not in cls._upload_cache:
            print(f"uploading to {host}")
            t0 = time.time()
            zipapp.create_archive(
                "remote_scripts",
            )
            conn.put(LIB_NAME, LIB_NAME)
            dt = time.time() - t0
            print(f"upload took {dt:.2f}s")
        cls._upload_cache.add(host)

    _info_cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_info(cls, conn: Info) -> Dict[str, Any]:
        host = conn.host
        if host not in cls._info_cache:
            # TODO: don't hardcode user
            info = run_remote_rpc(conn, "get_info", params=dict(user="pi"))
            cls._info_cache[host] = info
        return cls._info_cache[host]

    def _append_remote_script(
            self,
            user: Optional[str],
            rpc_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {"user": user, "payload": rpc_payload}

    def execute(self) -> List[Dict[str, Any]]:
        assert self.done is False
        if len(self.steps) == 0:
            return []

        self._upload_zip(self.conn)

        data = pickle.dumps(self.steps, 0)
        payload = b64encode(data).decode()

        cmd = f"python3 ./{LIB_NAME} stdin-rpc {payload}"
        commands = ", ".join(s['payload']['method'] for s in self.steps)
        print(f"Commands: {commands}")
        output = io.StringIO()

        if self.sudo:
            self.conn._c.sudo(cmd, out_stream=output)
        else:
            self.conn._c.run(cmd, out_stream=output)

        self.done = True

        return [
            pickle.loads(b64decode(s))
            for s in output.getvalue().split(",")
        ]


def run_remote_rpc(
        conn: "Info",
        method: str,
        params: Dict[str, Any],
        user: Optional[str] = None,
) -> Dict[str, Any]:
    r = Runner(conn)
    r.run_remote_rpc(method, params, user)
    result = r.execute()
    assert len(result) == 1
    return result[0]
