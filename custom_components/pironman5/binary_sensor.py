from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .entity import PironmanEntity


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator = entry.runtime_data

    if coordinator.supports("gpio_fan_state"):
        async_add_entities([
            PironmanFanState(coordinator, entry.entry_id)
        ])


class PironmanFanState(PironmanEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_name = "Fan Running"
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry_id,
    ):
        super().__init__(coordinator)

        self._attr_unique_id = f"{entry_id}_fan_running"

    @property
    def is_on(self):
        return bool(
            self.coordinator.data.get(
                "gpio_fan_state",
                0,
            )
        )
