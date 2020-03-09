import provision.settings as settings
from .service import Provision


class Taglist(Provision):
    name = "taglist"
    deps = ["consul"]

    def setup(self) -> None:
        tags = set(self.ctx.record['tags'] + settings.settings['common_tags'])

        content = "".join(t + "\n" for t in sorted(tags))

        self.ensure_file(
            path="/etc/taglist.txt",
            mode=0o644,
            user="root",
            group="root",
            content=content,
        )
