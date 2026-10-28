"""Safety tests for storage registry cleanup eligibility."""

import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components/pironman5"


def load_function(path, name, namespace):
    tree = ast.parse(path.read_text())
    selected = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == name
    ]
    exec(
        compile(
            ast.Module(body=selected, type_ignores=[]),
            str(path),
            "exec",
        ),
        namespace,
    )
    return namespace[name]


def storage_key_for_unique_suffix(suffix):
    if suffix.startswith("storage_") and suffix.endswith("_usage"):
        return suffix[len("storage_"):-len("_usage")]
    if suffix == "nvme_usage":
        return "nvme0n1"
    return None


eligible = load_function(
    COMPONENT / "storage_registry_cleanup.py",
    "eligible_storage_entities",
    {
        "storage_key_for_unique_suffix":
            storage_key_for_unique_suffix,
    },
)


def entity(device, entry="abc", platform="pironman5"):
    suffix = (
        "nvme_usage" if device == "nvme0n1"
        else f"storage_{device}_usage"
    )
    return SimpleNamespace(
        domain="sensor",
        platform=platform,
        config_entry_id=entry,
        unique_id=f"{entry}_{suffix}",
        entity_id=f"sensor.test_{device}",
    )


def check(entries, due, present=set(), allowed=set(), enabled=False):
    return eligible(
        entries,
        "abc",
        due,
        present,
        allowed,
        enabled=enabled,
    )


def test_disabled_by_default():
    assert check(
        [entity("sda")],
        {"sda"},
        allowed={"sda"},
    ) == {}


def test_approved_missing_device():
    assert check(
        [entity("sda")],
        {"sda"},
        allowed={"sda"},
        enabled=True,
    ) == {"sda": ["sensor.test_sda"]}


def test_present_device_protected():
    assert check(
        [entity("sda")],
        {"sda"},
        present={"sda"},
        allowed={"sda"},
        enabled=True,
    ) == {}


def test_unapproved_device_protected():
    assert check(
        [entity("sda")],
        {"sda"},
        enabled=True,
    ) == {}


def test_nvme_protected():
    assert check(
        [entity("nvme0n1")],
        {"nvme0n1"},
        allowed={"nvme0n1"},
        enabled=True,
    ) == {}


def test_other_integration_protected():
    assert check(
        [entity("sda", platform="other")],
        {"sda"},
        allowed={"sda"},
        enabled=True,
    ) == {}


def test_other_config_entry_protected():
    assert check(
        [entity("sda", entry="other")],
        {"sda"},
        allowed={"sda"},
        enabled=True,
    ) == {}
