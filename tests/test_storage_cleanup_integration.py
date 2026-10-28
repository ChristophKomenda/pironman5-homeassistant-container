"""Integration tests for the storage absence lifecycle."""

import ast
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components/pironman5"


class FakeStore:
    data = {}

    def __init__(self, hass, version, key):
        self.key = key

    async def async_load(self):
        return self.data.get(self.key)

    async def async_save(self, data):
        self.data[self.key] = data


def load_tracker():
    path = COMPONENT / "storage_cleanup.py"
    tree = ast.parse(path.read_text())

    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "StorageCleanupTracker"
    ]

    namespace = {
        "Store": FakeStore,
        "STORAGE_VERSION": 1,
        "CLEANUP_AFTER": timedelta(hours=24),
        "datetime": datetime,
        "timezone": timezone,
        "is_usb_candidate": lambda device: bool(
            re.fullmatch(r"sd[a-z]+", device)
        ),
    }

    exec(
        compile(
            ast.Module(body=classes, type_ignores=[]),
            str(path),
            "exec",
        ),
        namespace,
    )

    return namespace["StorageCleanupTracker"]


@pytest.fixture
def tracker_class():
    FakeStore.data = {}
    return load_tracker()


START = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_not_due_before_24_hours(tracker_class):
    tracker = tracker_class(None, "integration")

    await tracker.async_observe(
        {"sda"}, set(),
        now=START,
        absent_devices={"sda"},
    )

    due = await tracker.async_observe(
        {"sda"}, set(),
        now=START + timedelta(hours=23, minutes=59),
        absent_devices={"sda"},
    )

    assert due == set()


@pytest.mark.asyncio
async def test_due_after_24_hours(tracker_class):
    tracker = tracker_class(None, "integration")

    await tracker.async_observe(
        {"sda"}, set(),
        now=START,
        absent_devices={"sda"},
    )

    due = await tracker.async_observe(
        {"sda"}, set(),
        now=START + timedelta(hours=24),
        absent_devices={"sda"},
    )

    assert due == {"sda"}


@pytest.mark.asyncio
async def test_reconnect_prevents_cleanup(tracker_class):
    tracker = tracker_class(None, "integration")

    await tracker.async_observe(
        {"sda"}, set(),
        now=START,
        absent_devices={"sda"},
    )

    due = await tracker.async_observe(
        {"sda"}, {"sda"},
        now=START + timedelta(hours=25),
        absent_devices=set(),
    )

    assert due == set()
    assert tracker._missing == {}


@pytest.mark.asyncio
async def test_unknown_snapshot_does_not_trigger_cleanup(
    tracker_class,
):
    tracker = tracker_class(None, "integration")

    await tracker.async_observe(
        {"sda"}, set(),
        now=START,
        absent_devices={"sda"},
    )

    due = await tracker.async_observe(
        {"sda"}, set(),
        now=START + timedelta(hours=25),
        absent_devices=set(),
    )

    assert due == set()
    assert tracker._missing["sda"] == START


@pytest.mark.asyncio
async def test_restart_preserves_countdown(tracker_class):
    first = tracker_class(None, "integration")

    await first.async_observe(
        {"sda"}, set(),
        now=START,
        absent_devices={"sda"},
    )

    restarted = tracker_class(None, "integration")
    await restarted.async_load()

    due = await restarted.async_observe(
        {"sda"}, set(),
        now=START + timedelta(hours=25),
        absent_devices={"sda"},
    )

    assert due == {"sda"}


@pytest.mark.asyncio
async def test_forget_only_after_explicit_success(tracker_class):
    tracker = tracker_class(None, "integration")

    await tracker.async_observe(
        {"sda"}, set(),
        now=START,
        absent_devices={"sda"},
    )

    assert "sda" in tracker._missing

    await tracker.async_forget({"sda"})

    assert "sda" not in tracker._missing
