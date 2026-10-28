"""Conservative validation of Pironman storage API snapshots."""

import re

_STORAGE_TOTAL = re.compile(
    r"^disk_/dev/(?P<device>sd[a-z]+|nvme\d+n\d+)_total$"
)


def storage_snapshot_status(data, registered_devices):
    """Classify storage devices conservatively.

    Positive capacity confirms presence.
    None, zero, missing fields, and invalid values are unknown.

    The current API does not provide reliable evidence of physical
    device removal, so explicit absence is never reported.
    """
    if not isinstance(data, dict):
        return set(), set()

    totals = {}

    for key, value in data.items():
        if not isinstance(key, str):
            continue

        match = _STORAGE_TOTAL.fullmatch(key)
        if match is None:
            continue

        device = match.group("device")

        if value is None:
            totals[device] = None
        elif isinstance(value, bool):
            continue
        elif isinstance(value, (int, float)) and value >= 0:
            totals[device] = value

    present = {
        device
        for device, total in totals.items()
        if total is not None and total > 0
    }

    # None and zero are ambiguous API values, not proof
    # of physical USB device removal.
    # Until stable device identification is available,
    # never report an explicitly absent device.
    absent = set()

    return present, absent
