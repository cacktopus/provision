from typing import List, Dict, Any

import provision.consul_health_checks as consul_health_checks
from .service import Service


class Git(Service):
    name = "git"
    description = "git server"
    deps = ["consul"]
    port = 9418
    metrics_port = None

    def command_line(self) -> str:
        home = self.user_home()
        git_home = self.user_home("git")
        return f"/usr/bin/git daemon --reuseaddr --base-path={home} {git_home}"

    def consul_health_checks(self) -> List[Dict[str, Any]]:
        return [consul_health_checks.check_tcp(self.name, self.ctx.host, self.port)]

    def setup(self) -> None:
        self.ensure_dir(
            path=self.user_home("git"),
            mode=0o750,
            user=self.user,
            group=self.group,
        )

        for repo in ["heads.git", "rtunneld.git", "provision.git"]:
            path = self.home_for_user(self.user, "git", repo)
            self.runner.run_remote_rpc("new_git_repo", params=dict(path=path), user=self.user)

            self.ensure_file(
                path=self.user_home("git", repo, "git-daemon-export-ok"),
                mode=0o640,
                user=self.user,
                group=self.group,
                content="",
            )
