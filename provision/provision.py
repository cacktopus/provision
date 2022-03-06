import importlib
import inspect
import provision.actions as actions
import time
from fabric import Connection  # type: ignore
from networkx import topological_sort  # type: ignore

from .context import Context
from .info import Info
# TODO: turn of automatic updates
# TODO: turn of motd-news (chmod -x /etc/update-motd.d/*)
# TODO: sudo vi /etc/apt/apt.conf.d/20auto-upgrades
# TODO: install git
from .service import Service, Provision
from .settings import Settings


def register_all() -> None:
    for m in [
        "provision.system_setup",
        "provision.setup_user",
        "provision.packages",
        "provision.grafana",
        "provision.redis",
        "provision.prometheus",
        "provision.go",
        "provision.node_exporter",
        "provision.home",
        "provision.rtunneld",
        "provision.consul",
        "provision.consul_template",
        "provision.leds",
        "provision.git",
        "provision.boss",
        "provision.python_env",
        "provision.head",
        "provision.voices",
        "provision.boss_ui",
        "provision.camera",
        "provision.buildbot",
        "provision.gitweb",
        "provision.alertmanager",
        "provision.firewall",
        "provision.rtc",
        "provision.timesync",
        "provision.taglist",
        "provision.opencv",
        "provision.syncthing",
        "provision.shairport_sync",
        "provision.prometheus_discovery",
        "provision.logstream",
        "provision.ubuntu",
        "provision.power_monitor",
        "provision.serf",
        "provision.aht20",
        "provision.heads_cli",
        "provision.solar",
    ]:
        mod = importlib.import_module(m)

        register(mod)

    actions.add_dep("service-ready", "node-modules", "python-env", "opencv", "go", "buildbot")


def register(mod):
    for cls in mod.__dict__.values():
        if not inspect.isclass(cls):
            continue

        if cls in (Service, Provision):
            continue

        if issubclass(cls, Provision):
            target = cls()
            print(f"{target.deps} -> {target.action_name}")
            actions.Action(target.action_name, deps=target.deps)(target)


def main(settings: Settings) -> None:
    common_tags = frozenset(settings.common_tags)
    blacklist_tags = frozenset(settings.blacklist_tags)
    whitelist_tags = frozenset(settings.whitelist_tags)

    gateway = Connection(settings.deploy_gateway) if settings.deploy_gateway else None

    register_all()

    for host in settings.whitelist_hosts:
        record = settings.by_name[host]
        port = 22

        initial_password = record.initial_password
        ip = record.initial_ip or record.host + ".local"

        print(" {} ({}:{}) ".format(record.host, ip, port).center(80, "="))

        kw = dict(password=initial_password) if initial_password else dict()

        c = Connection(ip, user=record.sudo, port=port, connect_kwargs=kw, gateway=gateway, forward_agent=True)
        root_conn = Info(c)

        tags = set(record.tags) | common_tags

        all_actions = set(actions.actions.keys())

        # print(sorted(list(all_actions)))

        if whitelist_tags:
            white = set(whitelist_tags)
            # print(sorted(list(whitelist_tags)))
            missing = set(white) - all_actions
            if missing:
                raise Exception("Unknown whitelist tags: " + ", ".join(missing))
            tags &= white
        else:
            white = set()

        # print("tags", sorted(list(tags)))

        if blacklist_tags:
            black = set(blacklist_tags)
            missing = set(black) - all_actions
            if missing:
                raise Exception("Unknown whitelist tags: " + ", ".join(missing))
            tags -= (black - white)

        print("tags:", ", ".join(sorted(list(tags))))

        tag_ids = list(tags)

        ctx = Context(
            root_conn=root_conn,
            record=record,
            tags=tags,
            host=host,
            settings=settings,
        )

        order = list(topological_sort(actions.G))
        print("\n".join(order))

        print("=" * 80)

        with open("deps.dot", "w") as fp:
            print("digraph {", file=fp)
            for a, b in actions.G.edges:
                print(f'"{a}" -> "{b}"', file=fp)
            print("}", file=fp)

        missing_actions = ", ".join(sorted(set(tag_ids) - set(order)))

        if missing_actions:
            raise Exception(f"Unknown action for tags: {missing_actions}")

        start_at = settings.start_at
        if start_at:
            first = order.index(start_at)
            order = order[first:]

        print("-")
        print("\n".join(order))

        todo = [a for a in order if a in tag_ids]
        print("actions:", ", ".join(todo))

        times = {}

        for name in order:
            if name in tag_ids:
                t0 = time.time()
                print("=" * 80)
                print(f"Running: {name} ({host})")
                print("=" * 80)
                actions.actions[name](ctx)
                dt = time.time() - t0
                print(f"{name} completed in {dt:.2f}s")
                print("")
                times[name] = dt

        for v, k in sorted(((v, k) for k, v in times.items()), reverse=True):
            print(f"{k:20} {v:.2f}s")
        print("-" * 27)
        total: float = sum(times.values())
        print("{:20} {:.2f}s".format("total", total))
