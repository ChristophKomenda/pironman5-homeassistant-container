"""Pironman system sensors with dynamic storage discovery."""

import re

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers import entity_registry as er
from homeassistant.const import (
    PERCENTAGE,
    UnitOfDataRate,
    UnitOfFrequency,
    UnitOfInformation,
    UnitOfTemperature,
)

from .coordinator import PironmanCoordinator, available_storage_devices
from .entity import PironmanEntity


SENSORS = [
    ("cpu_temperature", "CPU Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, "cpu_temperature"),
    ("gpu_temperature", "GPU Temperature", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, "gpu_temperature"),
    ("cpu_usage", "CPU Usage", None, PERCENTAGE, "cpu_percent"),
    ("cpu_frequency", "CPU Frequency", None, UnitOfFrequency.MEGAHERTZ, "cpu_freq"),
    ("memory_usage", "Memory Usage", None, PERCENTAGE, "memory_percent"),
    ("memory_used", "Memory Used", SensorDeviceClass.DATA_SIZE, UnitOfInformation.BYTES, "memory_used"),
    ("network_download", "Network Download", SensorDeviceClass.DATA_RATE, UnitOfDataRate.BYTES_PER_SECOND, "network_download_speed"),
    ("network_upload", "Network Upload", SensorDeviceClass.DATA_RATE, UnitOfDataRate.BYTES_PER_SECOND, "network_upload_speed"),
    ("fan_speed", "Fan Speed", None, PERCENTAGE, "pwm_fan_speed"),
]

# Whole block devices only; partitions (nvme0n1p1, sda1) are excluded.
_STORAGE_KEY = re.compile(r"^disk_/dev/(nvme\d+n\d+|sd[a-z]+|mmcblk\d+)_percent$")
_LEGACY = {"nvme0n1": "nvme_usage", "nvme1n1": "nvme1_usage"}


def discover_storage(data):
    """Return present block devices; null placeholders do not count."""
    if not isinstance(data, dict):
        return {}
    return {
        device: f"disk_/dev/{device}_percent"
        for device in available_storage_devices(data)
    }


def discover_nvme(data):
    """Backward-compatible discovery helper for existing tests."""
    return {dev: key for dev, key in discover_storage(data).items() if dev.startswith("nvme")}


def storage_unique_suffix(device):
    """Preserve the original NVMe unique IDs from v1.2.0."""
    return _LEGACY.get(device, f"storage_{device}_usage")


def nvme_unique_suffix(device):
    """Keep the prototype's additional-NVMe naming convention."""
    return _LEGACY.get(device, f"nvme_{device}_usage")


def storage_key_for_unique_suffix(suffix):
    """Recover a device path from a registered entity's unique ID suffix."""
    for device, legacy in _LEGACY.items():
        if suffix == legacy:
            return device
    if suffix.startswith("storage_") and suffix.endswith("_usage"):
        device = suffix[len("storage_"):-len("_usage")]
        if re.fullmatch(r"(?:nvme\d+n\d+|sd[a-z]+|mmcblk\d+)", device):
            return device
    if suffix.startswith("nvme_nvme") and suffix.endswith("_usage"):
        device = suffix[len("nvme_"):-len("_usage")]
        if re.fullmatch(r"nvme\d+n\d+", device):
            return device
    return None


async def async_setup_entry(hass, entry, async_add_entities):
    """Register available sensors and discover newly reported NVMe drives."""
    coordinator: PironmanCoordinator = entry.runtime_data
    registry = er.async_get(hass)
    known = set()

    def registered(key):
        """Preserve existing registry entries even if hardware is absent."""
        return registry.async_get_entity_id(
            "sensor", "pironman5", f"{entry.entry_id}_{key}"
        ) is not None

    def discover():
        data = coordinator.data or {}
        entities = []
        for key, name, device_class, unit, data_key in SENSORS:
            if key in known:
                continue
            if key == "fan_speed" and not coordinator.supports("pwm_fan_speed"):
                continue
            known.add(key)
            entities.append(PironmanSensor(
                coordinator, entry.entry_id, key, name, device_class, unit, data_key
            ))

        # Only create storage sensors if the model supports storage. When the
        # API omits capabilities, coordinator.supports keeps legacy behavior.
        disks = {dev: f"disk_/dev/{dev}_percent" for dev in coordinator.storage_devices}
        for device, data_key in sorted(disks.items()):
            key = nvme_unique_suffix(device) if device.startswith("nvme") else storage_unique_suffix(device)
            if key in known:
                continue
            known.add(key)
            name = ("NVMe 0 Usage" if device == "nvme0n1" else
                    "NVMe 1 Usage" if device == "nvme1n1" else f"{device} Usage")
            entities.append(PironmanSensor(
                coordinator, entry.entry_id, key, name, None, PERCENTAGE, data_key,
                storage_device=device,
            ))

        # Restore ALL registered storage sensors, even if the drive is absent
        # at startup. This avoids losing previously configured automations.
        for reg_entity in er.async_entries_for_config_entry(registry, entry.entry_id):
            if reg_entity.domain != "sensor" or reg_entity.platform != "pironman5":
                continue
            prefix = f"{entry.entry_id}_"
            if not reg_entity.unique_id.startswith(prefix):
                continue
            key = reg_entity.unique_id[len(prefix):]
            device = storage_key_for_unique_suffix(key)
            if device is None or key in known:
                continue
            known.add(key)
            entities.append(PironmanSensor(
                coordinator, entry.entry_id, key, f"{device} Usage", None,
                PERCENTAGE, f"disk_/dev/{device}_percent", storage_device=device,
            ))

        if entities:
            async_add_entities(entities)

    async_add_entities([PironmanModelSensor(coordinator, entry.entry_id)])
    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))

    import asyncio
    import logging

    logger = logging.getLogger(__name__)
    tracking_task = None
    tracking_stopped = False
    tracking_pending = False
    reported_due_devices = set()

    async def track_storage():
        """Process pending storage updates without overlapping tracker writes."""
        nonlocal tracking_pending

        try:
            while tracking_pending and not tracking_stopped:
                tracking_pending = False

                try:
                    due_devices = await coordinator.async_track_storage_absence()

                    if tracking_stopped:
                        return

                    newly_due = due_devices - reported_due_devices

                    for device in sorted(newly_due):
                        logger.warning(
                            "Pironman storage cleanup dry-run: "
                            "device %s has reached the 24-hour absence threshold; "
                            "registry entities remain untouched",
                            device,
                        )

                    reported_due_devices.clear()
                    reported_due_devices.update(due_devices)

                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception(
                        "Pironman storage absence tracking failed"
                    )

        except asyncio.CancelledError:
            raise

    def schedule_storage_tracking():
        nonlocal tracking_task, tracking_pending

        if tracking_stopped or not coordinator.last_update_success:
            return

        tracking_pending = True

        if tracking_task is not None and not tracking_task.done():
            return

        tracking_task = hass.async_create_task(track_storage())

    def stop_storage_tracking():
        nonlocal tracking_stopped, tracking_pending
        tracking_stopped = True
        tracking_pending = False

        if tracking_task is not None and not tracking_task.done():
            tracking_task.cancel()

    entry.async_on_unload(
        coordinator.async_add_listener(schedule_storage_tracking)
    )
    entry.async_on_unload(stop_storage_tracking)

    schedule_storage_tracking()


class PironmanSensor(PironmanEntity, SensorEntity):
    """Expose a sensor backed by the coordinator's current API data."""

    def __init__(self, coordinator, entry_id, key, name, device_class, unit, data_key, storage_device=None):
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._data_key = data_key
        self._storage_device = storage_device
        self._attr_has_entity_name = True

    @property
    def available(self):
        """Treat missing readings as unavailable without deleting entities."""
        if not super().available:
            return False
        data = self.coordinator.data or {}
        if self._storage_device is not None:
            return self._storage_device in discover_storage(data) and data.get(self._data_key) is not None
        return data.get(self._data_key) is not None

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get(self._data_key)


class PironmanModelSensor(PironmanEntity, SensorEntity):
    """Model and detection method."""

    _attr_name = "Model"
    _attr_icon = "mdi:raspberry-pi"
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_model"

    @property
    def native_value(self):
        from .models import MODEL_NAMES
        return MODEL_NAMES.get(self.coordinator.model_key, "Unknown")

    @property
    def extra_state_attributes(self):
        return {
            "model_key": self.coordinator.model_key,
            "detection_source": self.coordinator.model_source,
        }
