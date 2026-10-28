"""Conservative validation of Pironman storage API snapshots."""

import re

_STORAGE_TOTAL = re.compile(
    r"^disk_/dev/(?P<device>sd[a-z]+|nvme\d+n\d+)_total$"
)


def storage_snapshot_status(data, registered_devices):
    """Return present and explicitly absent devices.

    A missing API field is never evidence that a device was removed.

    Explicit absence requires a reported total of None or zero.
    Invalid values are ignored.
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

    absent = {
        device
        for device in registered_devices
        if device in totals
        and (totals[device] is None or totals[device] == 0)
    }

    return present, absent
