"""Tests for conservative storage snapshot interpretation."""

import ast
import re
from pathlib import Path

SOURCE = (
    Path(__file__).resolve().parents[1]
    / "custom_components/pironman5/storage_snapshot.py"
)

namespace = {"re": re}
exec(
    compile(ast.parse(SOURCE.read_text()), str(SOURCE), "exec"),
    namespace,
)

check = namespace["storage_snapshot_status"]


def test_present_device():
    present, absent = check(
        {"disk_/dev/sda_total": 500000},
        {"sda"},
    )
    assert present == {"sda"}
    assert absent == set()


def test_none_total_is_unknown():
    present, absent = check(
        {"disk_/dev/sda_total": None},
        {"sda"},
    )
    assert present == set()
    assert absent == set()


def test_missing_field_not_absent():
    present, absent = check(
        {"disk_/dev/sdb_total": 500000},
        {"sda", "sdb"},
    )
    assert present == {"sdb"}
    assert absent == set()


def test_invalid_snapshot_not_absent():
    assert check(None, {"sda"}) == (set(), set())


def test_invalid_total_not_absent():
    assert check(
        {"disk_/dev/sda_total": "unknown"},
        {"sda"},
    ) == (set(), set())


def test_zero_total_is_unknown():
    assert check(
        {"disk_/dev/sda_total": 0},
        {"sda"},
    ) == (set(), set())


def test_nvme_none_total_is_unknown():
    assert check(
        {"disk_/dev/nvme0n1_total": None},
        {"nvme0n1"},
    ) == (set(), set())


def test_ambiguous_api_values_never_trigger_absence():
    """Unknown storage values must never trigger cleanup."""
    registered = {"sda", "sde", "sdf"}

    snapshots = [
        {
            "disk_/dev/sda_total": 500_000_000_000,
            "disk_/dev/sde_total": None,
            "disk_/dev/sdf_total": None,
        },
        {
            "disk_/dev/sda_total": 500_000_000_000,
            "disk_/dev/sde_total": 0,
            "disk_/dev/sdf_total": 0,
        },
        {
            "disk_/dev/sda_total": 500_000_000_000,
        },
    ]

    for snapshot in snapshots:
        present, absent = check(
            snapshot,
            registered,
        )

        assert "sda" in present
        assert absent == set()
