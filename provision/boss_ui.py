from .service import Provision


class NodeJS(Provision):
    name = "nodejs"
    deps = ["consul"]

    def setup(self) -> None:
        self.get_tar_archive()

        # TODO: below is pretty gross
        self.runner.run_remote_rpc("ensure_link", params=dict(
            src=self.build_home("builds", "nodejs", "prod", "bin", "node"),
            dst=self.build_home("bin", "node"),
        ), user="build")

        self.runner.run_remote_rpc("ensure_link", params=dict(
            src=self.build_home("builds", "nodejs", "prod", "bin", "npm"),
            dst=self.build_home("bin", "npm"),
        ), user="build")


class NodeModules(Provision):
    action_name = "node-modules"
    name = "node_modules"
    deps = ["nodejs"]
    repo = "heads"

    def setup(self) -> None:
        self.build()


class BossUI(Provision):
    name = "boss-ui"
    deps = ["service-ready", "node-modules"]
    repo = "heads"

    def setup(self) -> None:
        self.build()
