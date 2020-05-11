import requests

CONSUL_URL = "http://consul.service.consul:8500"


def put(path: str, data: str):
    path = path.lstrip("/")
    resp = requests.put(
        url=f"{CONSUL_URL}/v1/kv/{path}",
        data=data,
    )

    assert resp.status_code == 200, f"{resp.status_code} {resp.text}"
