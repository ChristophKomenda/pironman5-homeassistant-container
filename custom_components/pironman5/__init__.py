from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator import PironmanCoordinator

type PironmanConfigEntry = ConfigEntry[PironmanCoordinator]


PLATFORMS = [
    "sensor",
    "binary_sensor",
    "select",
    "light",
    "number",
    "switch",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PironmanConfigEntry,
) -> bool:
    """Set up Pironman 5 from a config entry."""
    coordinator = PironmanCoordinator(
        hass,
        entry,
        entry.options.get("host", entry.data["host"]),
        entry.options.get("port", entry.data["port"]),
    )

    from datetime import timedelta
    from .const import DEFAULT_SCAN_INTERVAL
    coordinator.update_interval = timedelta(seconds=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL))
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    await coordinator.storage_cleanup.async_load()
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    platforms = [*PLATFORMS]
    if entry.options.get("ir_enabled", False):
        platforms.append("infrared")
    coordinator.ir_platform_loaded = "infrared" in platforms
    await hass.config_entries.async_forward_entry_setups(
        entry,
        platforms,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: PironmanConfigEntry,
) -> bool:
    """Unload Pironman 5."""
    platforms = [*PLATFORMS]
    if getattr(entry.runtime_data, "ir_platform_loaded", False):
        platforms.append("infrared")
    return await hass.config_entries.async_unload_platforms(
        entry,
        platforms,
    )


async def async_update_options(hass: HomeAssistant, entry: PironmanConfigEntry) -> None:
    """Reload integration when user changes options."""
    await hass.config_entries.async_reload(entry.entry_id)
