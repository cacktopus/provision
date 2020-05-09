from .context import Context
from .run_remote_script import Runner
from .service import Provision
from .service_util import adduser


class BuildUser(Provision):
    name = "user(build)"
    deps = ["start"]

    def __call__(self, ctx: Context) -> None:
        runner = Runner(ctx.root_conn)
        adduser(ctx, runner, "build", [])
        runner.execute()


class PiUser(Provision):
    name = "user(pi)"
    deps = ["start", "user(build)"]

    def __call__(self, ctx: Context) -> None:
        runner = Runner(ctx.root_conn)
        adduser(ctx, runner, "pi", ["build"])
        runner.execute()


class RootUser(Provision):
    name = "user(root)"
    deps = ["start"]

    def __call__(self, ctx: Context) -> None:
        self.runner = Runner(ctx.root_conn)

        adduser(ctx, self.runner, "root", [])
        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename=".profile",
            line=". .bash_aliases",
        ))

        self.runner.execute()
