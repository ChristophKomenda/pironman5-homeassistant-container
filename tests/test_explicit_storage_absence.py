"""Tests for explicit storage absence tracking."""

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "custom_components/pironman5/storage_cleanup.py"
)


class FakeStore:
    saved = None

    def __init__(self, *args):
        self.data = {}

    async def async_load(self):
        return self.data

    async def async_save(self, data):
        self.data = data
        FakeStore.saved = data


def is_usb_candidate(device):
    import re
    return bool(re.fullmatch(r"sd[a-z]+", device))


tree = ast.parse(SOURCE.read_text())
selected = [
    node for node in tree.body
    if isinstance(node, ast.ClassDef)
    and node.name == "StorageCleanupTracker"
]

namespace = {
    "Store": FakeStore,
    "STORAGE_VERSION": 1,
    "CLEANUP_AFTER": timedelta(hours=24),
    "is_usb_candidate": is_usb_candidate,
    "datetime": datetime,
    "timezone": timezone,
}

exec(
    compile(
        ast.Module(body=selected, type_ignores=[]),
        str(SOURCE),
        "exec",
    ),
    namespace,
)

Tracker = namespace["StorageCleanupTracker"]
NOW = datetime(2026, 10, 28, 12, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_unknown_device_does_not_start_countdown():
    tracker = Tracker(None, "test")

    due = await tracker.async_observe(
        {"sda"},
        set(),
        now=NOW,
        absent_devices=set(),
    )

    assert due == set()
    assert tracker._missing == {}


@pytest.mark.asyncio
async def test_explicit_absence_starts_countdown():
    tracker = Tracker(None, "test")

    await tracker.async_observe(
        {"sda"},
        set(),
        now=NOW,
        absent_devices={"sda"},
    )

    assert tracker._missing["sda"] == NOW


@pytest.mark.asyncio
async def test_unknown_snapshot_preserves_timestamp():
    tracker = Tracker(None, "test")

    await tracker.async_observe(
        {"sda"},
        set(),
        now=NOW,
        absent_devices={"sda"},
    )

    due = await tracker.async_observe(
        {"sda"},
        set(),
        now=NOW + timedelta(hours=25),
        absent_devices=set(),
    )

    assert due == set()
    assert tracker._missing["sda"] == NOW


@pytest.mark.asyncio
async def test_reconnection_cancels_countdown():
    tracker = Tracker(None, "test")

    await tracker.async_observe(
        {"sda"},
        set(),
        now=NOW,
        absent_devices={"sda"},
    )

    due = await tracker.async_observe(
        {"sda"},
        {"sda"},
        now=NOW + timedelta(hours=25),
        absent_devices=set(),
    )

    assert due == set()
    assert tracker._missing == {}
