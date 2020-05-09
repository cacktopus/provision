from provision.settings import Settings

Settings(
    mainuser="jsu",
    network="10.1.0.0./24",

    env={
        "leds": {
            "NUM_LEDS": "263",
            "START_INDEX": "0",
            "ANIMATION": "rainbow",
        },
        "boss": {
            "GIN_MODE": "release"
        }
    },

    whitelist_hosts=[
        "base01",
        "base02",
        "base03",
    ],

    whitelist_tags=[
    ],

    blacklist_tags=[
    ],

    common_tags=[
        "user(build)",
        "user(pi)",
        "user(root)",
        "node-exporter",
        "packages",
        "packages2",
        "setup-host",
        "go",
        "buildbot",
        "firewall",
        "timesync",
    ],
)

