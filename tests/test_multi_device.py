"""Static regression checks for multiple Pironman config entries."""

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "pironman5"


def test_multiple_config_entries_allowed():
    manifest = json.loads(
        (COMPONENT / "manifest.json").read_text()
    )
    assert manifest.get("single_config_entry") is not True


def test_unique_id_uses_host():
    source = (COMPONENT / "config_flow.py").read_text()
    assert "async_set_unique_id" in source
    assert "user_input[CONF_HOST].strip()" in source
    assert "_abort_if_unique_id_configured()" in source


def test_entities_use_config_entry_id():
    source = (COMPONENT / "sensor.py").read_text()
    assert 'f"{entry_id}_{key}"' in source


def test_device_registry_uses_host():
    source = (COMPONENT / "coordinator.py").read_text()
    assert "identifiers={(DOMAIN, self.host)}" in source


def test_manifest_version():
    manifest = json.loads(
        (COMPONENT / "manifest.json").read_text()
    )
    assert manifest["version"] == "1.3.2"
