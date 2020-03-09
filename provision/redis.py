from typing import Optional, List, Dict, Any

import provision.consul_health_checks as consul_health_checks
from .service import Service


class Redis(Service):
    name = "redis"
    description = "redis db"
    deps = ["consul", "packages2"]
    port = 6379
    metrics_port = None

    def command_line(self) -> Optional[str]:
        return None  # note: run system redis

    def setup(self) -> None:
        pass

    def consul_health_checks(self) -> List[Dict[str, Any]]:
        return [consul_health_checks.check_tcp(self.name, self.ctx.host, self.port)]

    def register_service(self) -> None:
        self.register_service_with_consul(self.name, 6379)

        self.template(
            name="redis.conf",
            location="/etc/redis/redis.conf",
            user=self.user,
            group=self.group,
        )
