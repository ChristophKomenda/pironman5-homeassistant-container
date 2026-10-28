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


def test_explicitly_absent_device():
    present, absent = check(
        {"disk_/dev/sda_total": None},
        {"sda"},
    )
    assert present == set()
    assert absent == {"sda"}


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


def test_zero_total_means_explicit_absence():
    assert check(
        {"disk_/dev/sda_total": 0},
        {"sda"},
    ) == (set(), {"sda"})


def test_nvme_can_be_identified_but_not_deleted_here():
    assert check(
        {"disk_/dev/nvme0n1_total": None},
        {"nvme0n1"},
    ) == (set(), {"nvme0n1"})
