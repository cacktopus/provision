import subprocess

from .service import Provision


class SyncStatic(Provision):
    name = "sync-static"
    deps = ["host-ready"]

    def setup(self) -> None:
        settings = self.ctx.settings
        static = settings.shared_files_path
        assert static
        record = self.ctx.record
        ip = record.initial_ip or record.host

        self.ensure_dir(
            path=self.home_for_user("static", "shared"),
            mode=0o755,
            user="static",
            group="static",
        )

        if self.ctx.record.sync_exclude:
            exclude = " ".join(
                f"--exclude '{pat}'" for pat in sorted(list(self.ctx.record.sync_exclude))
            )
        else:
            exclude = " "

        delete = "--delete" if self.ctx.settings.sync_delete else ""

        cmd = f"rsync -a --progress {delete} --bwlimit {settings.sync_bwlimit} {static}/ {exclude} static@{ip}:shared/"
        print(f"running {cmd}")

        retcode = subprocess.call(cmd, shell=True)
        if retcode != 0:
            raise Exception("sync-static failed")
