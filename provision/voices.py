from typing import List, Dict

from .service import Service


class Voices(Service):
    name = "voices"
    description = "Do you sometimes hear voices?"
    deps = ["service-ready"]

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["audio"]

    def env(self) -> Dict[str, str]:
        return {
            "INSTANCE": "head-40",  # TODO
        }

    def command_line(self) -> str:
        return " ".join([
            self.prod_path("env", "bin", "python3"),
            "voices.py"
        ])

    def working_dir(self) -> str:
        return self.prod_path()

    def setup(self) -> None:
        self.build()

    def register_service(self) -> None:
        head = self.ctx.record.kv['head']
        assert self.port is not None
        self.register_service_with_consul(self.name, self.port, tags=[head])
