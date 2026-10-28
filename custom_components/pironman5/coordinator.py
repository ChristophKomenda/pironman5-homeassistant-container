from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import API_PATH, DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import AUTO, CONF_MODEL, MODEL_NAMES, resolve_model

_LOGGER = logging.getLogger(__name__)


class PironmanCoordinator(
    DataUpdateCoordinator[dict[str, Any]]
):
    """Coordinator for the Pironman 5 API."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        host: str,
        port: int,
    ) -> None:
        """Initialize the Pironman coordinator."""
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}{API_PATH}"
        self.session = async_get_clientsession(hass)

        self.device_info_data: dict[str, Any] = {}
        self.peripherals: frozenset[str] | None = None
        self.model_key: str | None = None
        self.model_source = "unknown"
        self._model_selection = config_entry.options.get(
            CONF_MODEL, config_entry.data.get(CONF_MODEL, AUTO)
        )

        super().__init__(
            hass,
            _LOGGER,
            name="Pironman 5",
            config_entry=config_entry,
            update_interval=timedelta(
                seconds=DEFAULT_SCAN_INTERVAL
            ),
        )

    async def _async_setup(self) -> None:
        """Fetch static device information."""
        await self.async_get_device_info()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        info = self.device_info_data

        name = MODEL_NAMES.get(self.model_key) or info.get("name", "Pironman 5")

        return DeviceInfo(
            identifiers={(DOMAIN, self.host)},
            name=name,
            manufacturer="SunFounder",
            model=name,
            sw_version=info.get("version"),
        )

    async def async_get_device_info(
        self,
    ) -> dict[str, Any]:
        """Fetch static device information."""
        try:
            async with self.session.get(
                f"{self.base_url}/get-device-info",
                timeout=5,
            ) as response:
                response.raise_for_status()
                result = await response.json()

            if not result.get("status"):
                raise UpdateFailed(
                    "Pironman API returned status=false "
                    "for get-device-info"
                )

            raw_data = result.get("data")
            if not isinstance(raw_data, dict):
                raise UpdateFailed("Invalid get-device-info data")
            self.device_info_data = raw_data

            peripherals = raw_data.get("peripherals")
            if isinstance(peripherals, list) and all(
                isinstance(item, str) for item in peripherals
            ):
                self.peripherals = frozenset(peripherals)
            else:
                self.peripherals = None

            self.model_key, self.model_source = resolve_model(
                raw_data, self._model_selection
            )
            if self.model_key is None:
                _LOGGER.warning(
                    "Pironman model could not be determined from API metadata; "
                    "select the model manually in integration options"
                )
            return self.device_info_data

        except Exception as err:
            raise UpdateFailed(
                f"Unable to get Pironman device information: {err}"
            ) from err

    def supports(self, peripheral: str) -> bool:
        """Check whether the connected device supports a peripheral.

        If the API does not expose capabilities, preserve the
        existing integration behavior for backward compatibility.
        """
        if self.peripherals is None:
            return True

        return peripheral in self.peripherals

    async def _async_update_data(
        self,
    ) -> dict[str, Any]:
        """Fetch current Pironman data."""
        try:
            async with self.session.get(
                f"{self.base_url}/get-data",
                timeout=5,
            ) as response:
                response.raise_for_status()
                data_result = await response.json()

            async with self.session.get(
                f"{self.base_url}/get-config",
                timeout=5,
            ) as response:
                response.raise_for_status()
                config_result = await response.json()

            if not data_result.get("status"):
                raise UpdateFailed(
                    "Pironman API returned status=false "
                    "for get-data"
                )

            if not config_result.get("status"):
                raise UpdateFailed(
                    "Pironman API returned status=false "
                    "for get-config"
                )

            data = data_result.get(
                "data",
                {},
            )

            config = config_result.get(
                "data",
                {},
            ).get(
                "system",
                {},
            )

            return {
                **data,
                **config,
            }

        except Exception as err:
            raise UpdateFailed(
                f"Unable to communicate with Pironman API: {err}"
            ) from err

    async def post(
        self,
        endpoint: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Send a command to the Pironman API."""
        url = f"{self.base_url}/{endpoint}"

        try:
            async with self.session.post(
                url,
                json=payload,
                timeout=5,
            ) as response:
                response.raise_for_status()
                result = await response.json()

            if not result.get("status"):
                raise UpdateFailed(
                    f"Pironman API rejected request: {result}"
                )

            await self.async_request_refresh()

            return result

        except Exception as err:
            raise UpdateFailed(
                f"Pironman API request failed: {err}"
            ) from err
