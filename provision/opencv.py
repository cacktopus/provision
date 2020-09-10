from .service import Provision


class OpenCV(Provision):
    name = "opencv"
    deps = ["consul", "packages", "packages2"]

    def setup(self) -> None:
        self.runner.run_remote_rpc("install_deb", params=dict(
            url="https://theheads.sfo2.digitaloceanspaces.com/build/opencv_4.4.0-2_armhf.deb",
            digest="3dd6ec5f4ff498b7da733ea978fcf02196707bbf8df71e8d02a0b5b4d21de37b",
            pkg_name="opencv",
            version="4.4.0-2",
        ))
