"""Coordinator for the local Pironman REST API."""

from datetime import timedelta
import logging
import re
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_PATH, DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import AUTO, CONF_MODEL, MODEL_NAMES, resolve_model
from .storage_cleanup import StorageCleanupTracker

_LOGGER = logging.getLogger(__name__)
_STORAGE_PERCENT_KEY = re.compile(r"^disk_/dev/(nvme\d+n\d+|sd[a-z]+|mmcblk\d+)_percent$")


def available_storage_devices(data: dict[str, Any] | None) -> frozenset[str]:
    """Return present whole block devices, ignoring vendor null placeholders."""
    if not isinstance(data, dict):
        return frozenset()
    found = set()
    for key in data:
        if not isinstance(key, str) or not (match := _STORAGE_PERCENT_KEY.fullmatch(key)):
            continue
        device = match.group(1)
        total = data.get(f"disk_/dev/{device}_total")
        if isinstance(total, (int, float)) and not isinstance(total, bool) and total > 0:
            found.add(device)
    return frozenset(found)


class PironmanCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for the Pironman 5 API."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}{API_PATH}"
        self.session = async_get_clientsession(hass)
        self.device_info_data: dict[str, Any] = {}
        self.peripherals: frozenset[str] | None = None
        self.model_key: str | None = None
        self.model_source = "unknown"
        self.storage_devices: frozenset[str] = frozenset()
        self.storage_cleanup = StorageCleanupTracker(
            hass,
            config_entry.entry_id,
        )
        self._model_selection = config_entry.options.get(
            CONF_MODEL, config_entry.data.get(CONF_MODEL, AUTO)
        )
        super().__init__(
            hass, _LOGGER, name="Pironman 5", config_entry=config_entry,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_setup(self) -> None:
        await self.async_get_device_info()

    @property
    def device_info(self) -> DeviceInfo:
        info = self.device_info_data
        name = MODEL_NAMES.get(self.model_key) or info.get("name", "Pironman 5")
        return DeviceInfo(
            identifiers={(DOMAIN, self.host)}, name=name,
            manufacturer="SunFounder", model=name, sw_version=info.get("version"),
        )

    async def async_get_device_info(self) -> dict[str, Any]:
        try:
            async with self.session.get(f"{self.base_url}/get-device-info", timeout=5) as response:
                response.raise_for_status()
                result = await response.json()
            if not result.get("status"):
                raise UpdateFailed("Pironman API returned status=false for get-device-info")
            raw_data = result.get("data")
            if not isinstance(raw_data, dict):
                raise UpdateFailed("Invalid get-device-info data")
            self.device_info_data = raw_data
            peripherals = raw_data.get("peripherals")
            if isinstance(peripherals, list) and all(isinstance(item, str) for item in peripherals):
                self.peripherals = frozenset(peripherals)
            else:
                self.peripherals = None
            self.model_key, self.model_source = resolve_model(raw_data, self._model_selection)
            if self.model_key is None:
                _LOGGER.warning(
                    "Pironman model could not be determined from API metadata; "
                    "select the model manually in integration options"
                )
            return self.device_info_data
        except Exception as err:
            raise UpdateFailed(f"Unable to get Pironman device information: {err}") from err

    def supports(self, peripheral: str) -> bool:
        if self.peripherals is None:
            return True
        return peripheral in self.peripherals

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with self.session.get(f"{self.base_url}/get-data", timeout=5) as response:
                response.raise_for_status()
                data_result = await response.json()
            async with self.session.get(f"{self.base_url}/get-config", timeout=5) as response:
                response.raise_for_status()
                config_result = await response.json()
            if not data_result.get("status"):
                raise UpdateFailed("Pironman API returned status=false for get-data")
            if not config_result.get("status"):
                raise UpdateFailed("Pironman API returned status=false for get-config")
            data = data_result.get("data", {})
            config_data = config_result.get("data", {})
            if not isinstance(data, dict) or not isinstance(config_data, dict):
                raise UpdateFailed("Invalid Pironman API payload")
            config = config_data.get("system", {})
            if not isinstance(config, dict):
                raise UpdateFailed("Invalid Pironman configuration payload")
            merged = {**data, **config}
            self.storage_devices = (
                available_storage_devices(merged) if self.supports("storage") else frozenset()
            )
            return merged
        except Exception as err:
            raise UpdateFailed(f"Unable to communicate with Pironman API: {err}") from err

    async def async_track_storage_absence(self) -> set[str]:
        """Track missing registered storage sensors after a valid refresh."""
        from homeassistant.helpers import entity_registry as er
        from .sensor import storage_key_for_unique_suffix

        if not self.last_update_success or not self.supports("storage"):
            return set()

        data = self.data
        if not isinstance(data, dict):
            return set()

        # Never interpret an incomplete API response as disk removal.
        if not any(
            isinstance(key, str) and key.startswith("disk_/dev/")
            for key in data
        ):
            return set()

        registry = er.async_get(self.hass)
        prefix = f"{self.config_entry.entry_id}_"
        registered = set()

        for entity in er.async_entries_for_config_entry(
            registry, self.config_entry.entry_id
        ):
            if entity.domain != "sensor" or entity.platform != "pironman5":
                continue
            if not entity.unique_id.startswith(prefix):
                continue

            suffix = entity.unique_id[len(prefix):]
            device = storage_key_for_unique_suffix(suffix)
            if device is not None:
                registered.add(device)

        from .storage_snapshot import storage_snapshot_status

        present, absent = storage_snapshot_status(
            data,
            registered,
        )

        return await self.storage_cleanup.async_observe(
            registered,
            present,
            absent_devices=absent,
        )

    async def post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint}"
        try:
            async with self.session.post(url, json=payload, timeout=5) as response:
                response.raise_for_status()
                result = await response.json()
            if not result.get("status"):
                raise UpdateFailed(f"Pironman API rejected request: {result}")
            await self.async_request_refresh()
            return result
        except Exception as err:
            raise UpdateFailed(f"Pironman API request failed: {err}") from err
