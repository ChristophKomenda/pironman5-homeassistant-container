"""Regression tests for Pironman sensor display metadata without Home Assistant installed."""

import ast
from pathlib import Path
from types import SimpleNamespace

SENSOR = Path(__file__).resolve().parents[1] / "custom_components/pironman5/sensor.py"


class _Names:
    def __getattr__(self, name):
        return name


class _PironmanEntity:
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def available(self):
        return True


def _load_sensor_definitions():
    tree = ast.parse(SENSOR.read_text(encoding="utf-8"))
    selection = [
        node for node in tree.body
        if (isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SENSORS"
            for target in node.targets
        )) or (isinstance(node, ast.ClassDef) and node.name == "PironmanSensor")
    ]
    names = _Names()
    scope = {
        "PironmanEntity": _PironmanEntity,
        "SensorEntity": object,
        "SensorDeviceClass": names,
        "SensorStateClass": names,
        "UnitOfTemperature": names,
        "UnitOfFrequency": names,
        "UnitOfDataRate": names,
        "UnitOfInformation": names,
        "PERCENTAGE": "%",
    }
    exec(compile(ast.Module(body=selection, type_ignores=[]), str(SENSOR), "exec"), scope)
    return scope


def _new_sensor(key):
    scope = _load_sensor_definitions()
    descriptor = next(row for row in scope["SENSORS"] if row[0] == key)
    coordinator = SimpleNamespace(data={descriptor[4]: 1250000})
    return scope["PironmanSensor"](
        coordinator, "existing_entry_id", *descriptor
    )


def test_network_native_bytes_and_suggested_kilobytes():
    for key in ("network_download", "network_upload"):
        sensor = _new_sensor(key)
        assert sensor._attr_native_unit_of_measurement == "BYTES_PER_SECOND"
        assert sensor._attr_device_class == "DATA_RATE"
        assert sensor._attr_suggested_unit_of_measurement == "KILOBYTES_PER_SECOND"
        assert sensor._attr_suggested_display_precision == 1
        assert sensor.native_value == 1250000
        assert sensor._attr_unique_id == f"existing_entry_id_{key}"


def test_memory_used_stays_in_bytes_and_displays_gib():
    sensor = _new_sensor("memory_used")
    assert sensor._attr_native_unit_of_measurement == "BYTES"
    assert sensor._attr_suggested_unit_of_measurement == "GIBIBYTES"
    assert sensor._attr_suggested_display_precision == 2


def test_cpu_frequency_in_mhz_and_preferred_ghz():
    sensor = _new_sensor("cpu_frequency")
    assert sensor._attr_device_class == "FREQUENCY"
    assert sensor._attr_native_unit_of_measurement == "MEGAHERTZ"
    assert sensor._attr_suggested_unit_of_measurement == "GIGAHERTZ"
    assert sensor._attr_suggested_display_precision == 2


def test_pwm_fan_is_rpm_not_percent():
    sensor = _new_sensor("fan_speed")
    assert sensor._attr_native_unit_of_measurement == "rpm"
    assert sensor._attr_suggested_display_precision == 0
    assert sensor.native_value == 1250000


def test_measurement_statistics_for_numeric_sensors():
    for key in ("cpu_temperature", "gpu_temperature", "cpu_usage",
                "cpu_frequency", "memory_usage", "memory_used",
                "network_download", "network_upload", "fan_speed"):
        assert _new_sensor(key)._attr_state_class == "MEASUREMENT"
