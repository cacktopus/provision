from typing import List, Dict, Optional

from .service import Service


class ShairportSync(Service):
    name = "shairport-sync"
    description = "shairport-sync"
    deps = ["service-ready"]
    port = None

    def extra_groups(self) -> List[str]:
        return super().extra_groups() + ["audio"]

    def command_line(self) -> str:
        instance = self.ctx.record.kv['speaker-name']
        return " ".join([
            self.exe(),
            "-a", instance,
            "--", "-d", "hw:1",
        ])

    def setup(self) -> None:
        self.get_tar_archive()

    def systemd_extra(self) -> Optional[Dict[str, str]]:
        return {"ExecStartPre": "/bin/sleep 10"}
