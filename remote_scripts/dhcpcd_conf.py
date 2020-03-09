import re
from collections import OrderedDict

pat = re.compile(r"\s+|=")

DHCPCD_CFG = "/etc/dhcpcd.conf"


def static_interface(
        name: str,
        ip_address: str,
        routers: str,
        domain_name_servers: str
):
    return """
interface {name}
static ip_address={ip_address}
static routers={routers}
static domain_name_servers={domain_name_servers}
""".format(**locals()).strip()


def split_sections(lines):
    current_section, start = "global", 0

    for pos, line in enumerate(lines):
        line = line.strip().split("#", maxsplit=1)[0]
        parts = re.split(pat, line)
        if len(parts) == 2 and parts[0] == "interface":
            yield current_section, "".join(lines[start:pos])
            current_section = "interface " + parts[1]
            start = pos

    yield current_section, "".join(lines[start:pos + 1])


def dhcpcd_conf(interfaces):
    with open(DHCPCD_CFG) as fp:
        lines = fp.readlines()

    sections = OrderedDict(split_sections(lines))

    for iface in interfaces:
        section_key = "interface {}".format(iface['name'])
        sections[section_key] = static_interface(**iface)

    result = "\n\n".join(text.strip() for text in sections.values()) + "\n"
    if result == "".join(lines):
        return

    with open(DHCPCD_CFG, "w") as fp:
        fp.write(result)
