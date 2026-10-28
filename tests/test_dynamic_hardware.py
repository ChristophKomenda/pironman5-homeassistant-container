"""Storage discovery regression tests; no Home Assistant installation required."""
import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "custom_components/pironman5"


def extract(path, names, globals_):
    source = ROOT.joinpath(path).read_text()
    tree = ast.parse(source)
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    exec(compile(ast.Module(body=selected, type_ignores=[]), path, "exec"), globals_)
    return globals_


sensor = extract("sensor.py", {"discover_storage", "discover_nvme", "storage_unique_suffix", "nvme_unique_suffix", "storage_key_for_unique_suffix"}, {
    "re": re, "_STORAGE_KEY": re.compile(r"^disk_/dev/(nvme\d+n\d+|sd[a-z]+)_percent$"),
    "_LEGACY": {"nvme0n1": "nvme_usage", "nvme1n1": "nvme1_usage"},
})
coordinator = extract("coordinator.py", {"available_storage_devices"}, {
    "re": re, "Any": object, "_STORAGE_PERCENT_KEY": re.compile(r"^disk_/dev/(nvme\d+n\d+|sd[a-z]+)_percent$"),
})


# Make the coordinator discovery helper available to the isolated
# sensor functions, matching the import used by sensor.py.
sensor["available_storage_devices"] = coordinator["available_storage_devices"]


def sample():
    return {
        "disk_/dev/nvme0n1_total": 250074470809,
        "disk_/dev/nvme0n1_mounted": 0,
        "disk_/dev/nvme0n1_percent": 0.0,
        "disk_/dev/nvme1n1_total": 491113861120,
        "disk_/dev/nvme1n1_mounted": 1,
        "disk_/dev/nvme1n1_percent": 22.74,
        "disk_/dev/sda_total": 500074283008,
        "disk_/dev/sda_percent": 0.04,
        "disk_/dev/sdb_total": 528592896,
        "disk_/dev/sdb_percent": 15.37,
        "disk_/dev/sdc_total": 502921060352,
        "disk_/dev/sdc_percent": 2.67,
        "disk_/dev/sdd_total": None,
        "disk_/dev/sdd_percent": None,
        "disk_/dev/sde_total": None,
        "disk_/dev/sde_percent": None,
    }


def test_real_vendor_payload():
    expected = {"nvme0n1", "nvme1n1", "sda", "sdb", "sdc"}
    assert set(sensor["discover_storage"](sample())) == expected
    assert coordinator["available_storage_devices"](sample()) == frozenset(expected)


def test_unmounted_nvme_still_present():
    assert "nvme0n1" in sensor["discover_storage"](sample())


def test_null_placeholders_not_present():
    assert "sdd" not in sensor["discover_storage"](sample())
    assert "sde" not in sensor["discover_storage"](sample())


def test_partitions_ignored():
    data = sample() | {"disk_/dev/nvme0n1p1_percent": 12, "disk_/dev/nvme0n1p1_total": 100,
                       "disk_/dev/sda1_percent": 12, "disk_/dev/sda1_total": 100}
    assert set(sensor["discover_storage"](data)) == {"nvme0n1", "nvme1n1", "sda", "sdb", "sdc"}


def test_new_disk_appears_in_next_snapshot():
    before = sample()
    after = before | {"disk_/dev/sdf_percent": 4, "disk_/dev/sdf_total": 100000}
    assert "sdf" not in coordinator["available_storage_devices"](before)
    assert "sdf" in coordinator["available_storage_devices"](after)


def test_removed_disk_disappears_from_snapshot():
    before = sample()
    after = before | {"disk_/dev/sdc_percent": None, "disk_/dev/sdc_total": None}
    assert "sdc" in coordinator["available_storage_devices"](before)
    assert "sdc" not in coordinator["available_storage_devices"](after)


def test_legacy_ids():
    assert sensor["nvme_unique_suffix"]("nvme0n1") == "nvme_usage"
    assert sensor["nvme_unique_suffix"]("nvme1n1") == "nvme1_usage"
    assert sensor["nvme_unique_suffix"]("nvme2n1") == "nvme_nvme2n1_usage"


def test_unique_ids_and_restore():
    assert sensor["storage_unique_suffix"]("sda") == "storage_sda_usage"
    assert sensor["storage_unique_suffix"]("sdb") == "storage_sdb_usage"
    for suffix, device in [("nvme_usage", "nvme0n1"), ("nvme1_usage", "nvme1n1"),
                           ("nvme_nvme2n1_usage", "nvme2n1"), ("storage_sda_usage", "sda")]:
        assert sensor["storage_key_for_unique_suffix"](suffix) == device
    assert sensor["storage_key_for_unique_suffix"]("storage_sda1_usage") is None


def test_invalid_data():
    for value in [None, [], {}, {"disk_/dev/sda_percent": None, "disk_/dev/sda_total": None}]:
        assert sensor["discover_storage"](value) == {}
        assert coordinator["available_storage_devices"](value) == frozenset()
