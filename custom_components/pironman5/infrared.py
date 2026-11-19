"""Optional native infrared receiver for the Pironman host-side raw IR bridge.

This uses the HA infrared platform (available in recent Home Assistant versions).
The optional host bridge sends pironman5_ir_raw_received events to HA's REST API.
"""
from __future__ import annotations

import logging

from homeassistant.components.infrared import InfraredReceivedSignal, InfraredReceiverEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import PironmanCoordinator

_LOGGER = logging.getLogger(__name__)
EVENT_NAME = "pironman5_ir_raw_received"
CONF_IR_DEVICE_ID = "ir_device_id"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Attach the opt-in IR receiver to the existing Pironman device."""
    coordinator: PironmanCoordinator = entry.runtime_data
    device_id = str(entry.options.get(CONF_IR_DEVICE_ID, "")).strip()
    if not device_id:
        _LOGGER.warning("IR enabled but device ID missing; configure the IR device ID")
        return
    async_add_entities([PironmanIRReceiver(entry, coordinator, device_id)])


class PironmanIRReceiver(InfraredReceiverEntity):
    """Receive full raw frames, preserving RC5 toggle and held-key frames."""

    _attr_has_entity_name = True
    _attr_name = "IR Receiver"

    def __init__(self, entry: ConfigEntry, coordinator: PironmanCoordinator, device_id: str) -> None:
        self._device_id = device_id
        self._attr_unique_id = f"{entry.entry_id}_ir_receiver"
        self._attr_device_info = coordinator.device_info
        self._unsub = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._unsub = self.hass.bus.async_listen(EVENT_NAME, self._handle_event)

    @callback
    def _handle_event(self, event: Event) -> None:
        data = event.data
        if data.get("device_id") != self._device_id:
            return
        timings = data.get("timings")
        if not valid_timings(timings):
            _LOGGER.debug("Discarded invalid raw IR frame for %s", self._device_id)
            return
        modulation = data.get("modulation")
        if type(modulation) is not int or not 20_000 <= modulation <= 100_000:
            modulation = None
        # No deduplication here! RC5's toggle bit distinguishes separate presses,
        # and HAIR needs the full frames to interpret long button holds.
        self._handle_received_signal(
            InfraredReceivedSignal(timings=timings, modulation=modulation)
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub is not None:
            self._unsub()
            self._unsub = None
        await super().async_will_remove_from_hass()


def valid_timings(values: object) -> bool:
    """Validate complete alternating signed pulse/space LIRC frames."""
    if not isinstance(values, list) or not 8 <= len(values) <= 512:
        return False
    for idx, value in enumerate(values):
        if type(value) is not int or value == 0 or abs(value) > 1_000_000:
            return False
        if (value > 0) != (idx % 2 == 0):
            return False
    return True
