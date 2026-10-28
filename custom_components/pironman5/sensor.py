from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)

from homeassistant.const import (
    PERCENTAGE,
    UnitOfDataRate,
    UnitOfFrequency,
    UnitOfInformation,
    UnitOfTemperature,
)

from .coordinator import PironmanCoordinator
from .entity import PironmanEntity


SENSORS = [
    (
        "cpu_temperature",
        "CPU Temperature",
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "cpu_temperature",
    ),
    (
        "gpu_temperature",
        "GPU Temperature",
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        "gpu_temperature",
    ),
    (
        "cpu_usage",
        "CPU Usage",
        None,
        PERCENTAGE,
        "cpu_percent",
    ),
    (
        "cpu_frequency",
        "CPU Frequency",
        None,
        UnitOfFrequency.MEGAHERTZ,
        "cpu_freq",
    ),
    (
        "memory_usage",
        "Memory Usage",
        None,
        PERCENTAGE,
        "memory_percent",
    ),
    (
        "memory_used",
        "Memory Used",
        SensorDeviceClass.DATA_SIZE,
        UnitOfInformation.BYTES,
        "memory_used",
    ),
    (
        "nvme_usage",
        "NVMe 0 Usage",
        None,
        PERCENTAGE,
        "disk_/dev/nvme0n1_percent",
    ),
    (
        "nvme1_usage",
        "NVMe 1 Usage",
        None,
        PERCENTAGE,
        "disk_/dev/nvme1n1_percent",
    ),
    (
        "network_download",
        "Network Download",
        SensorDeviceClass.DATA_RATE,
        UnitOfDataRate.BYTES_PER_SECOND,
        "network_download_speed",
    ),
    (
        "network_upload",
        "Network Upload",
        SensorDeviceClass.DATA_RATE,
        UnitOfDataRate.BYTES_PER_SECOND,
        "network_upload_speed",
    ),
    (
        "fan_speed",
        "Fan Speed",
        None,
        PERCENTAGE,
        "pwm_fan_speed",
    ),
]


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):
    coordinator: PironmanCoordinator = entry.runtime_data

    entities = []

    for key, name, device_class, unit, data_key in SENSORS:
        if key == "fan_speed" and not coordinator.supports(
            "pwm_fan_speed"
        ):
            continue

        entities.append(
            PironmanSensor(
                coordinator,
                entry.entry_id,
                key,
                name,
                device_class,
                unit,
                data_key,
            )
        )

    entities.append(PironmanModelSensor(coordinator, entry.entry_id))
    async_add_entities(entities)


class PironmanSensor(PironmanEntity, SensorEntity):
    def __init__(
        self,
        coordinator,
        entry_id,
        key,
        name,
        device_class,
        unit,
        data_key,
    ):
        super().__init__(coordinator)

        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._data_key = data_key
        self._attr_has_entity_name = True

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get(self._data_key)



class PironmanModelSensor(PironmanEntity, SensorEntity):
    """Model and detection method (unknown when vendor metadata is insufficient)."""
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
