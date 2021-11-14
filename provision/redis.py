from typing import Optional, List, Dict, Any

import provision.consul_health_checks as consul_health_checks
from .service import Service


class Redis(Service):
    name = "redis"
    description = "redis db"
    deps = ["consul"]
    port = 6379
    metrics_port = None

    def command_line(self) -> Optional[str]:
        return None  # note: run system redis

    def setup(self) -> None:
        self.template(
            name="redis.conf",
            location="/etc/redis/redis.conf",
            user=self.user,
            group=self.group,
        )
