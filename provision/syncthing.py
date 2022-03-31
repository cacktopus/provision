from provision.run_remote_script import Runner
from provision.service_util import adduser

from .service import Provision


class Syncthing(Provision):
    name = "syncthing"
    deps = ["user(build)", "packages2"]

    metrics_port = None

    def setup(self) -> None:
        runner = Runner(self.ctx.root_conn)
        adduser(self.ctx, runner, "syncthing", [])
        runner.execute()
