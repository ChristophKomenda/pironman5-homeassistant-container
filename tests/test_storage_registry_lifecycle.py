"""Behavior tests for guarded storage registry cleanup."""

import ast
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "custom_components"
    / "pironman5"
    / "storage_registry_cleanup.py"
)


def storage_key_for_unique_suffix(suffix):
    if suffix.startswith("storage_") and suffix.endswith("_usage"):
        return suffix[len("storage_"):-len("_usage")]
    if suffix == "nvme_usage":
        return "nvme0n1"
    return None


def load_functions():
    tree = ast.parse(SOURCE.read_text())
    selected = [
        node for node in tree.body
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        )
        and node.name in {
            "eligible_storage_entities",
            "async_cleanup_storage_registry",
        }
    ]

    namespace = {
        "storage_key_for_unique_suffix":
            storage_key_for_unique_suffix,
        "_LOGGER": logging.getLogger(__name__),
    }

    exec(
        compile(
            ast.Module(body=selected, type_ignores=[]),
            str(SOURCE),
            "exec",
        ),
        namespace,
    )

    return namespace


class FakeRegistry:
    def __init__(self, entities):
        self.entities = {
            entity.entity_id: entity
            for entity in entities
        }
        self.removed = []
        self.fail_for = set()

    def async_get(self, entity_id):
        return self.entities.get(entity_id)

    def async_remove(self, entity_id):
        if entity_id in self.fail_for:
            raise RuntimeError("Simulated registry failure")

        self.entities.pop(entity_id)
        self.removed.append(entity_id)


class FakeEntityRegistryModule:
    def __init__(self, registry):
        self.registry = registry

    def async_get(self, hass):
        return self.registry

    def async_entries_for_config_entry(
        self, registry, entry_id
    ):
        return [
            entity
            for entity in registry.entities.values()
            if entity.config_entry_id == entry_id
        ]


def entity(device, entry_id="abc"):
    return SimpleNamespace(
        entity_id=f"sensor.test_{device}",
        domain="sensor",
        platform="pironman5",
        config_entry_id=entry_id,
        unique_id=f"{entry_id}_storage_{device}_usage",
    )


@pytest.fixture
def cleanup_env():
    namespace = load_functions()

    def make(entities):
        registry = FakeRegistry(entities)
        namespace["er"] = FakeEntityRegistryModule(registry)

        return (
            namespace["async_cleanup_storage_registry"],
            registry,
        )

    return make


@pytest.mark.asyncio
async def test_removes_approved_missing_sensor(cleanup_env):
    cleanup, registry = cleanup_env([entity("sda")])

    removed = await cleanup(
        None, "abc", {"sda"}, set(), {"sda"},
        enabled=True,
        is_device_present=lambda device: False,
    )

    assert removed == {"sda"}
    assert registry.removed == ["sensor.test_sda"]
    assert registry.async_get("sensor.test_sda") is None


@pytest.mark.asyncio
async def test_reconnected_device_is_not_removed(cleanup_env):
    cleanup, registry = cleanup_env([entity("sda")])

    removed = await cleanup(
        None, "abc", {"sda"}, {"sda"}, {"sda"},
        enabled=True,
        is_device_present=lambda device: False,
    )

    assert removed == set()
    assert registry.removed == []
    assert registry.async_get("sensor.test_sda") is not None


@pytest.mark.asyncio
async def test_registry_error_does_not_report_success(cleanup_env):
    cleanup, registry = cleanup_env([entity("sda")])
    registry.fail_for.add("sensor.test_sda")

    removed = await cleanup(
        None, "abc", {"sda"}, set(), {"sda"},
        enabled=True,
        is_device_present=lambda device: False,
    )

    assert removed == set()
    assert registry.removed == []
    assert registry.async_get("sensor.test_sda") is not None


@pytest.mark.asyncio
async def test_disabled_cleanup_does_nothing(cleanup_env):
    cleanup, registry = cleanup_env([entity("sda")])

    removed = await cleanup(
        None, "abc", {"sda"}, set(), {"sda"},
    )

    assert removed == set()
    assert registry.removed == []


@pytest.mark.asyncio
async def test_no_due_devices_does_nothing(cleanup_env):
    cleanup, registry = cleanup_env([entity("sda")])

    removed = await cleanup(
        None, "abc", set(), set(), {"sda"},
        enabled=True,
        is_device_present=lambda device: False,
    )

    assert removed == set()
    assert registry.removed == []


@pytest.mark.asyncio
async def test_foreign_config_entry_is_protected(cleanup_env):
    cleanup, registry = cleanup_env([
        entity("sda", entry_id="other")
    ])

    removed = await cleanup(
        None, "abc", {"sda"}, set(), {"sda"},
        enabled=True,
        is_device_present=lambda device: False,
    )

    assert removed == set()
    assert registry.removed == []


@pytest.mark.asyncio
async def test_unapproved_sensor_is_protected(cleanup_env):
    cleanup, registry = cleanup_env([entity("sda")])

    removed = await cleanup(
        None, "abc", {"sda"}, set(), set(),
        enabled=True,
        is_device_present=lambda device: False,
    )

    assert removed == set()
    assert registry.removed == []


@pytest.mark.asyncio
async def test_missing_live_checker_prevents_deletion(cleanup_env):
    cleanup, registry = cleanup_env([entity("sda")])

    removed = await cleanup(
        None, "abc", {"sda"}, set(), {"sda"},
        enabled=True,
    )

    assert removed == set()
    assert registry.removed == []


@pytest.mark.asyncio
async def test_multiple_entities_removed_for_one_device(cleanup_env):
    first = entity("sda")
    second = SimpleNamespace(
        entity_id="sensor.test_sda_temperature",
        domain="sensor",
        platform="pironman5",
        config_entry_id="abc",
        unique_id="abc_storage_sda_usage",
    )

    # The fake registry uses entity IDs as keys.
    cleanup, registry = cleanup_env([first, second])

    removed = await cleanup(
        None, "abc", {"sda"}, set(), {"sda"},
        enabled=True,
        is_device_present=lambda device: False,
    )

    assert removed == {"sda"}
    assert set(registry.removed) == {
        "sensor.test_sda",
        "sensor.test_sda_temperature",
    }


@pytest.mark.asyncio
async def test_reconnect_during_cleanup_stops_remaining_removals(
    cleanup_env,
):
    first = entity("sda")
    second = SimpleNamespace(
        entity_id="sensor.test_sda_second",
        domain="sensor",
        platform="pironman5",
        config_entry_id="abc",
        unique_id="abc_storage_sda_usage",
    )

    cleanup, registry = cleanup_env([first, second])
    checks = 0

    def presence(device):
        nonlocal checks
        checks += 1
        return checks >= 2

    removed = await cleanup(
        None, "abc", {"sda"}, set(), {"sda"},
        enabled=True,
        is_device_present=presence,
    )

    assert removed == set()
    assert len(registry.removed) == 1
