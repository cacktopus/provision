import json
import os
from typing import Dict, Any

import requests


class Unset:
    pass


class Client:
    def get(self, path: str) -> Dict[str, Any]:
        token = os.environ["VAULT_TOKEN"]

        resp = requests.get(
            url=f"http://127.0.0.1:8200/v1/kv/data/{path}",
            headers={
                "X-Vault-Token": token,
            }
        )

        assert resp.status_code == 200, f"{path} {resp.status_code}, {resp.text}"

        body = json.loads(resp.text)
        result: Dict[str, Any] = body['data']['data']
        return result
