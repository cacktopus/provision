from .service import Provision


class RTC(Provision):
    name = "rtc"
    deps = ["service-ready"]

    def setup(self) -> None:
        self.runner.run_remote_rpc("ensure_line_in_file", params=dict(
            filename="/boot/config.txt",
            line="dtoverlay=i2c-rtc,ds3231",
        ))

        self.template(
            name="hwclock-set",
            location="/lib/udev/hwclock-set",
            user="root",
            group="root",
            mode=0o755,
        )
