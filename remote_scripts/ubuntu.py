from setup_user import ensure_line_in_file


def ubuntu_setup():
    # ensure_line_in_file
    ensure_line_in_file(
        "/etc/sudoers.d/90-cloud-init-users",
        "pi ALL=(ALL) NOPASSWD:ALL",
    )
