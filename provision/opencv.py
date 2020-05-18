from .service import Provision


class OpenCV(Provision):
    name = "opencv"
    deps = ["consul", "packages", "packages2"]

    def setup(self) -> None:
        self.runner.run_remote_rpc("install_deb", params=dict(
            url="https://theheads.sfo2.digitaloceanspaces.com/opencv_4.2.0-2_all.deb",
            digest="b4cc7837a3e576a1882e99583ba6d3a9dfcf63ffc12cbc88f83ebafe086603a0",
            pkg_name="opencv",
            version="4.2.0-2",
        ))
