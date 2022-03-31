from typing import List

from .service import Service


class Voices(Service):
    name = "voices"
    description = "Do you sometimes hear voices?"
    deps = ["service-ready"]
    repo = "heads"

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["audio"]

    def command_line(self) -> str:
        return self.exe()

    def working_dir(self) -> str:
        return self.prod_path()

    def setup(self) -> None:
        self.get_tar_bz_archive()
