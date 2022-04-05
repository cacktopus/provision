from typing import List

from .service import Service
from .systemd import ServiceConfig


class Head(Service):
    name = "head"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["i2c", "gpio", "audio"]

    def working_dir(self) -> str:
        return self.prod_path()

    def setup(self) -> None:
        self.get_tar_archive()
        self.enable_i2c()

    def systemd_args(self) -> ServiceConfig:
        return ServiceConfig(
            exec_start=self.exe(),
            description="this is the head",
            type="simple",  # TODO: notify?
            after=["network.target"],
        )

    def instance_name(self) -> str:
        # consider moving this out of provision/serf and into the app itself
        return self.ctx.record.env["head"]["INSTANCE"]
