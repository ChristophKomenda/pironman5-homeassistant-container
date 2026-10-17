"""Switch controls for Pironman 5."""

from homeassistant.components.switch import SwitchEntity

from .entity import PironmanEntity
from .oled import PironmanOLED


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities(
        [
            PironmanOLEDEnabledSwitch(coordinator, entry.entry_id),
            PironmanOLEDAlwaysOnSwitch(coordinator, entry.entry_id),
        ]
    )


class PironmanOLEDEnabledSwitch(PironmanEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "OLED"
    _attr_icon = "mdi:monitor"

    def __init__(self, coordinator, entry_id) -> None:
        super().__init__(coordinator)
        self.oled = PironmanOLED(coordinator)
        self._attr_unique_id = f"{entry_id}_oled_enabled"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("oled_enable", False))

    async def async_turn_on(self, **kwargs) -> None:
        await self.oled.set_enabled(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.oled.set_enabled(False)


class PironmanOLEDAlwaysOnSwitch(PironmanEntity, SwitchEntity):
    """Disable the OLED sleep timer without disabling the OLED itself.

    The SunFounder OLED addon interprets oled_sleep_timeout=0 as
    unlimited runtime. Switching back restores the most recent positive
    timeout observed during this Home Assistant session, or 10 seconds.
    """

    _attr_has_entity_name = True
    _attr_name = "OLED Always On"
    _attr_icon = "mdi:monitor-eye"

    def __init__(self, coordinator, entry_id) -> None:
        super().__init__(coordinator)
        self.oled = PironmanOLED(coordinator)
        self._attr_unique_id = f"{entry_id}_oled_always_on"
        self._previous_timeout = 10

    @property
    def available(self) -> bool:
        return (
            super().available
            and "oled_sleep_timeout" in (self.coordinator.data or {})
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("oled_sleep_timeout") == 0

    def _handle_coordinator_update(self) -> None:
        timeout = (self.coordinator.data or {}).get("oled_sleep_timeout")
        if isinstance(timeout, (int, float)) and not isinstance(timeout, bool) and timeout > 0:
            self._previous_timeout = int(timeout)
        super()._handle_coordinator_update()

    async def async_turn_on(self, **kwargs) -> None:
        timeout = (self.coordinator.data or {}).get("oled_sleep_timeout")
        if isinstance(timeout, (int, float)) and not isinstance(timeout, bool) and timeout > 0:
            self._previous_timeout = int(timeout)
        await self.oled.set_sleep_timeout(0)

    async def async_turn_off(self, **kwargs) -> None:
        await self.oled.set_sleep_timeout(self._previous_timeout)
