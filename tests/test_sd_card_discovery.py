"""Regression tests for Raspberry Pi SD-card storage discovery."""

import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "custom_components/pironman5"


def load_function(filename, name, namespace):
    tree = ast.parse((ROOT / filename).read_text())
    selected = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    assert len(selected) == 1
    exec(
        compile(ast.Module(body=selected, type_ignores=[]), filename, "exec"),
        namespace,
    )
    return namespace[name]


def test_sd_card_discovery():
    namespace = {
        "re": re,
        "Any": object,
        "_STORAGE_PERCENT_KEY": re.compile(
            r"^disk_/dev/(nvme\d+n\d+|sd[a-z]+|mmcblk\d+)_percent$"
        ),
    }

    discover = load_function(
        "coordinator.py",
        "available_storage_devices",
        namespace,
    )

    data = {
        "disk_/dev/mmcblk0_total": 251815749632,
        "disk_/dev/mmcblk0_percent": 7.99,
        "disk_/dev/mmcblk0p1_total": 536870912,
        "disk_/dev/mmcblk0p1_percent": 10.0,
    }

    assert discover(data) == frozenset({"mmcblk0"})


def test_sd_card_unique_id():
    suffix = load_function(
        "sensor.py",
        "storage_unique_suffix",
        {"_LEGACY": {"nvme0n1": "nvme_usage", "nvme1n1": "nvme1_usage"}},
    )

    assert suffix("mmcblk0") == "storage_mmcblk0_usage"


def test_sd_card_registry_restore():
    restore = load_function(
        "sensor.py",
        "storage_key_for_unique_suffix",
        {
            "re": re,
            "_LEGACY": {
                "nvme0n1": "nvme_usage",
                "nvme1n1": "nvme1_usage",
            },
        },
    )

    assert restore("storage_mmcblk0_usage") == "mmcblk0"
    assert restore("storage_mmcblk0p1_usage") is None
