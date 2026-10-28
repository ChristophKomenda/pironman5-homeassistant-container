"""Safely remove explicitly approved stale storage sensors."""

import logging

from homeassistant.helpers import entity_registry as er

from .sensor import storage_key_for_unique_suffix

_LOGGER = logging.getLogger(__name__)


def eligible_storage_entities(
    entries,
    entry_id: str,
    due_devices: set[str],
    present_devices: set[str],
    allowed_devices: set[str],
    *,
    enabled: bool = False,
) -> dict[str, list[str]]:
    """Return device-to-entity mappings eligible for removal."""
    if not enabled:
        return {}

    candidates = (
        set(due_devices)
        & set(allowed_devices)
        - set(present_devices)
    )

    prefix = f"{entry_id}_"
    result = {}

    for entity in entries:
        if entity.domain != "sensor":
            continue

        if entity.platform != "pironman5":
            continue

        if entity.config_entry_id != entry_id:
            continue

        if not entity.unique_id.startswith(prefix):
            continue

        suffix = entity.unique_id[len(prefix):]
        device = storage_key_for_unique_suffix(suffix)

        if device not in candidates:
            continue

        # Never remove native PCIe NVMe sensor entities.
        if not device.startswith("sd"):
            continue

        result.setdefault(device, []).append(entity.entity_id)

    return result


async def async_cleanup_storage_registry(
    hass,
    entry_id: str,
    due_devices: set[str],
    present_devices: set[str],
    allowed_devices: set[str],
    *,
    enabled: bool = False,
    is_device_present=None,
) -> set[str]:
    """Remove approved registry entries; return successful devices."""
    if not enabled or not due_devices:
        return set()

    registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(
        registry, entry_id
    )

    candidates = eligible_storage_entities(
        entries,
        entry_id,
        due_devices,
        present_devices,
        allowed_devices,
        enabled=enabled,
    )

    removed = set()

    for device, entity_ids in candidates.items():
        # A live presence check is mandatory before deleting entities.
        # Without it, fail closed.
        if is_device_present is None:
            continue

        all_removed = True

        for entity_id in entity_ids:
            try:
                if is_device_present(device):
                    all_removed = False
                    break

                entity = registry.async_get(entity_id)
                if entity is None:
                    all_removed = False
                    continue

                if (
                    entity.config_entry_id != entry_id
                    or entity.platform != "pironman5"
                    or entity.domain != "sensor"
                    or not entity.unique_id.startswith(f"{entry_id}_")
                    or storage_key_for_unique_suffix(
                        entity.unique_id[len(entry_id) + 1:]
                    ) != device
                ):
                    all_removed = False
                    continue

                registry.async_remove(entity_id)

            except Exception:
                all_removed = False
                _LOGGER.exception(
                    "Unable to remove stale storage sensor %s",
                    entity_id,
                )

        if all_removed:
            removed.add(device)

    return removed
