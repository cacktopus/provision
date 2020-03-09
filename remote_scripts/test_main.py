import base64
import gzip
import json

from rpc import call


def encode(method: str, **args) -> str:
    json_str = json.dumps({"method": method, "params": args, }).encode()
    return base64.b64encode(gzip.compress(json_str, 9)).decode()


def main():
    payload = encode(
        'get_tar_archive',
        url="https://github.com/prometheus/prometheus/releases/download/v2.4.3/prometheus-2.4.3.linux-arm64.tar.gz",
        digest="796372ef8966182ac87b927c8b97ed05ff0856f54e82a9c9bc35464cd87dbe32",
        binaries=['prometheus', 'promtool'],
    )
    print(payload)
    call(payload)


if __name__ == '__main__':
    main()
