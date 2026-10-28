from homeassistant.components.number import (
    NumberEntity,
    NumberMode,
)

from .entity import PironmanEntity
from .oled import PironmanOLED


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = entry.runtime_data

    entities = []

    if coordinator.supports("ws2812"):
        entities.append(PironmanRGBSpeed(coordinator, entry.entry_id))

    if coordinator.supports("oled"):
        entities.append(
            PironmanOLEDSleepTimeout(coordinator, entry.entry_id)
        )

    async_add_entities(entities)


class PironmanRGBSpeed(PironmanEntity, NumberEntity):
    _attr_name = "RGB Effect Speed"
    _attr_has_entity_name = True
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator,
        entry_id,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = f"{entry_id}_rgb_speed"

    @property
    def native_value(self):
        return self.coordinator.data.get(
            "rgb_speed",
            50,
        )

    async def async_set_native_value(self, value):
        await self.coordinator.post(
            "set-rgb-speed",
            {"speed": int(value)},
        )


class PironmanOLEDSleepTimeout(
    PironmanEntity,
    NumberEntity,
):
    _attr_name = "OLED Sleep Timeout"
    _attr_has_entity_name = True
    _attr_native_min_value = 0
    _attr_native_max_value = 3600
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "s"
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:timer-outline"

    def __init__(
        self,
        coordinator,
        entry_id,
    ):
        super().__init__(coordinator)

        self.oled = PironmanOLED(coordinator)

        self._attr_unique_id = f"{entry_id}_oled_sleep_timeout"

    @property
    def native_value(self):
        return self.coordinator.data.get(
            "oled_sleep_timeout",
            10,
        )

    async def async_set_native_value(self, value):
        await self.oled.set_sleep_timeout(
            int(value)
        )

        await self.coordinator.async_request_refresh()
