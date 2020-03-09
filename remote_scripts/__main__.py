import getpass
import os
import pickle
import sys
from base64 import b64decode, b64encode
from subprocess import check_output

import functions
import rpc
from build_utils import cd
from util import log, timeit


def run_step(description: str, payload: str) -> str:
    decoded = b64decode(payload)
    msg = pickle.loads(decoded)
    method = getattr(functions, msg['method'])
    user = getpass.getuser()
    home = os.path.expanduser(f"~{user}")
    keys = ", ".join(msg['params'].keys())
    log(f" --- {description}: [ {msg['method']} ] as {user} ({keys})")
    with cd(home):
        result = method(**msg['params'])
        encoded = b64encode(pickle.dumps(result, 0)).decode()
        return encoded


def main() -> None:
    cmd = sys.argv[1]

    if cmd == "call":
        rpc.call(*sys.argv[2:])

    elif cmd == "rpc-step":
        payload = sys.argv[2]
        encoded = run_step("rpc-step", payload)
        sys.stdout.write(encoded)

    elif cmd == "stdin-rpc":
        payload = sys.argv[2]
        decoded = b64decode(payload)
        steps = pickle.loads(decoded)

        results = []

        for step in steps:
            user = step['user']
            msg = step['payload']
            current_user = check_output(["id", "--user", "--name"]).decode().strip()

            step_payload = b64encode(pickle.dumps(msg, 0)).decode()

            args = ["python3", sys.argv[0], "rpc-step", step_payload]

            if user is not None and user != current_user:
                args = ["sudo", "-u", user] + args
                with timeit("rpc-step"):
                    result = check_output(args).decode()
                results.append(result)

            else:
                with timeit("rpc-int"):
                    result = run_step("rpc-int", step_payload)
                results.append(result)

        sys.stdout.write(",".join(results))

    else:
        assert 0, "unknown command"


if __name__ == '__main__':
    main()
