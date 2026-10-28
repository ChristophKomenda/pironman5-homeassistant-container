"""Isolated tests for persistent storage cleanup tracking."""

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re

import pytest

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "custom_components/pironman5/storage_cleanup.py"
)


class FakeStore:
    data = {}

    def __init__(self, hass, version, key):
        self.key = key

    async def async_load(self):
        return self.data.get(self.key)

    async def async_save(self, value):
        self.data[self.key] = value


source_tree = ast.parse(SOURCE.read_text())
selected = [
    node for node in source_tree.body
    if (
        isinstance(node, (ast.ClassDef, ast.FunctionDef))
        and node.name in {"StorageCleanupTracker", "is_usb_candidate"}
    )
]
namespace = {
    "Store": FakeStore,
    "datetime": datetime,
    "timedelta": timedelta,
    "timezone": timezone,
    "STORAGE_VERSION": 1,
    "CLEANUP_AFTER": timedelta(hours=24),
    "USB_DEVICE_PATTERN": re.compile(r"sd[a-z]+", re.ASCII),
}
exec(
    compile(ast.Module(body=selected, type_ignores=[]), str(SOURCE), "exec"),
    namespace,
)
Tracker = namespace["StorageCleanupTracker"]

START = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def clear_store():
    FakeStore.data.clear()


@pytest.mark.asyncio
async def test_missing_device_starts_timer():
    tracker = Tracker(None, "test")
    await tracker.async_load()

    due = await tracker.async_observe({"sda"}, set(), now=START)

    assert due == set()
    assert "sda" in tracker._missing


@pytest.mark.asyncio
async def test_not_due_before_24_hours():
    tracker = Tracker(None, "test")
    await tracker.async_observe({"sda"}, set(), now=START)

    due = await tracker.async_observe(
        {"sda"}, set(), now=START + timedelta(hours=23, minutes=59)
    )
    assert due == set()


@pytest.mark.asyncio
async def test_due_after_24_hours():
    tracker = Tracker(None, "test")
    await tracker.async_observe({"sda"}, set(), now=START)

    due = await tracker.async_observe(
        {"sda"}, set(), now=START + timedelta(hours=24)
    )
    assert due == {"sda"}


@pytest.mark.asyncio
async def test_reconnect_cancels_cleanup():
    tracker = Tracker(None, "test")
    await tracker.async_observe({"sda"}, set(), now=START)

    due = await tracker.async_observe(
        {"sda"}, {"sda"}, now=START + timedelta(hours=25)
    )
    assert due == set()
    assert "sda" not in tracker._missing


@pytest.mark.asyncio
async def test_restart_preserves_timestamp():
    first = Tracker(None, "test")
    await first.async_observe({"sda"}, set(), now=START)

    restarted = Tracker(None, "test")
    await restarted.async_load()

    due = await restarted.async_observe(
        {"sda"}, set(), now=START + timedelta(hours=25)
    )
    assert due == {"sda"}


@pytest.mark.asyncio
async def test_invalid_snapshot_does_not_start_or_complete_cleanup():
    tracker = Tracker(None, "test")
    await tracker.async_observe({"sda"}, set(), now=START)

    due = await tracker.async_observe(
        {"sda", "sdb"},
        set(),
        now=START + timedelta(hours=25),
        snapshot_valid=False,
    )
    assert due == set()
    assert "sdb" not in tracker._missing


@pytest.mark.asyncio
async def test_nvme_is_never_tracked():
    tracker = Tracker(None, "test")

    due = await tracker.async_observe(
        {"nvme0n1"}, set(), now=START
    )
    assert due == set()
    assert tracker._missing == {}


@pytest.mark.asyncio
async def test_forget_after_successful_cleanup():
    tracker = Tracker(None, "test")
    await tracker.async_observe({"sda"}, set(), now=START)

    await tracker.async_forget({"sda"})

    assert tracker._missing == {}
    restarted = Tracker(None, "test")
    await restarted.async_load()
    assert restarted._missing == {}
