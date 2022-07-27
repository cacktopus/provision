import os
from hashlib import sha256

from .service import Provision


class OpenCV(Provision):
    name = "opencv"
    deps = ["serf"]

    def setup(self) -> None:
        machine = self.info['machine']

        arch = {
            "armv7l": "armhf",
            "aarch64": "arm64",
            "armv6l": "armv6",
        }[machine]

        pkg_name = f"opencv_4.5.5-2_{arch}.deb"

        pkg_file = os.path.join(self.ctx.settings.shared_files_path, "builds", arch, pkg_name)

        with open(pkg_file, "rb") as f:
            digest = sha256(f.read()).hexdigest()

        self.runner.run_remote_rpc("install_deb", params=dict(
            url=f"file:///home/static/shared/builds/{arch}/{pkg_name}",
            digest=digest,
            pkg_name="opencv",
            version="4.5.5-2",
            public_keys=self.ctx.settings.verify_pubkeys,
        ))
