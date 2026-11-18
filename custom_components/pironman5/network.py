"""Parse optional Pironman get-ips responses without HA dependencies."""
import re

_INTERFACE = re.compile(r"^[A-Za-z0-9_.:-]{1,32}$")


def extract_ip_addresses(payload):
    """Return interface -> IP string without MAC addresses or other metadata."""
    if not isinstance(payload, dict):
        return {}
    ips = payload.get("ips")
    if not isinstance(ips, dict):
        ips = {key[3:]: value for key, value in payload.items()
               if isinstance(key, str) and key.startswith("ip_")}
    result = {}
    for interface, address in ips.items():
        if not isinstance(interface, str) or not _INTERFACE.fullmatch(interface):
            continue
        if not isinstance(address, str) or not address.strip():
            continue
        result[interface] = address.strip()[:256]
        if len(result) >= 16:
            break
    return result
