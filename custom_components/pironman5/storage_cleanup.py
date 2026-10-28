"""Persistent absence tracking for dynamically discovered USB storage."""

from datetime import datetime, timedelta, timezone
import re

from homeassistant.helpers.storage import Store

STORAGE_VERSION = 1
CLEANUP_AFTER = timedelta(hours=24)
USB_DEVICE_PATTERN = re.compile(r"sd[a-z]+", re.ASCII)


def is_usb_candidate(device: str) -> bool:
    """Identify dynamic sdX-style storage paths.

    Note: sdX paths do not prove the physical bus is USB.
    """
    return bool(USB_DEVICE_PATTERN.fullmatch(device))


class StorageCleanupTracker:
    """Track missing storage paths across Home Assistant restarts."""

    def __init__(self, hass, entry_id: str):
        self._store = Store(
            hass,
            STORAGE_VERSION,
            f"pironman5.storage_cleanup.{entry_id}",
        )
        self._missing: dict[str, datetime] = {}

    async def async_load(self) -> None:
        """Restore previously recorded absence timestamps."""
        saved = await self._store.async_load() or {}
        missing = saved.get("missing", {})

        if not isinstance(missing, dict):
            return

        for device, timestamp in missing.items():
            if not isinstance(device, str) or not is_usb_candidate(device):
                continue
            if not isinstance(timestamp, str):
                continue

            try:
                parsed = datetime.fromisoformat(timestamp)
            except ValueError:
                continue

            if parsed.tzinfo is None:
                continue

            self._missing[device] = parsed.astimezone(timezone.utc)

    async def async_observe(
        self,
        registered_devices: set[str],
        present_devices: set[str],
        *,
        now: datetime | None = None,
        snapshot_valid: bool = True,
    ) -> set[str]:
        """Update absence state and return paths eligible for cleanup.

        Call only after a successful, trustworthy storage snapshot.
        This method does not delete entities.
        """
        if not snapshot_valid:
            return set()

        now = now or datetime.now(timezone.utc)
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        now = now.astimezone(timezone.utc)

        registered = {
            device for device in registered_devices
            if is_usb_candidate(device)
        }
        present = {
            device for device in present_devices
            if is_usb_candidate(device)
        }

        changed = False

        for device in tuple(self._missing):
            if device in present or device not in registered:
                del self._missing[device]
                changed = True

        for device in registered - present:
            if device not in self._missing:
                self._missing[device] = now
                changed = True

        if changed:
            await self._store.async_save({
                "missing": {
                    device: timestamp.isoformat()
                    for device, timestamp in sorted(self._missing.items())
                }
            })

        return {
            device
            for device, timestamp in self._missing.items()
            if device in registered
            and device not in present
            and now - timestamp >= CLEANUP_AFTER
        }

    async def async_forget(self, devices: set[str]) -> None:
        """Forget paths only after registry cleanup succeeds."""
        changed = False

        for device in devices:
            if device in self._missing:
                del self._missing[device]
                changed = True

        if changed:
            await self._store.async_save({
                "missing": {
                    device: timestamp.isoformat()
                    for device, timestamp in sorted(self._missing.items())
                }
            })
