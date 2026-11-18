"""Allowlisted and privacy-conscious Home Assistant diagnostics."""
from homeassistant.core import HomeAssistant
from .const import DOMAIN


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry) -> dict:
    """Export non-sensitive metadata only; no IP, MAC, host, config or logs."""
    coordinator = entry.runtime_data
    info = coordinator.device_info_data
    return {
        "integration_domain": DOMAIN,
        "model_key": coordinator.model_key,
        "model_source": coordinator.model_source,
        "software_version": info.get("version"),
        "reported_peripherals": sorted(coordinator.peripherals) if coordinator.peripherals is not None else None,
        "network_interfaces": sorted(coordinator.network_addresses),
        "storage_devices": sorted(coordinator.storage_devices),
        "last_update_success": coordinator.last_update_success,
    }
