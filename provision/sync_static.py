import subprocess

from .service import Provision


class SyncStatic(Provision):
    name = "sync-static"
    deps = ["host-ready"]

    def setup(self) -> None:
        settings = self.ctx.settings
        static = settings.static_files_path
        assert static
        record = self.ctx.record
        ip = record.initial_ip or record.host

        exclude = " ".join(
            f"--exclude '{pat}'" for pat in sorted(list(self.ctx.record.sync_exclude))
        )

        cmd = f"rsync -a --progress --bwlimit {settings.sync_bwlimit} {static}/ {exclude} static@{ip}:"
        print(f"running {cmd}")

        retcode = subprocess.call(cmd, shell=True)
        if retcode != 0:
            raise Exception("sync-static failed")
