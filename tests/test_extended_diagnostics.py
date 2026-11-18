"""v1.4.0 pure Python regression tests; no HA installation necessary."""
import ast
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "pironman5"


def load(name):
    spec = importlib.util.spec_from_file_location(name + "_test", ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_vendor_network_payload():
    parse = load("network").extract_ip_addresses
    data = {"ips": {"eth0": "192.168.1.22", "wlan0": "192.168.1.23"},
            "mac_eth0": "00:11:22:33:44:55"}
    assert parse(data) == {"eth0": "192.168.1.22", "wlan0": "192.168.1.23"}


def test_network_fallback_and_invalid_inputs():
    parse = load("network").extract_ip_addresses
    assert parse({"ip_eth0": "10.0.0.2", "mac_eth0": "secret"}) == {"eth0": "10.0.0.2"}
    assert parse({"ips": ["invalid"]}) == {}
    assert parse(None) == {}
    assert parse({"ips": {"bad/name": "1.2.3.4", "eth0": None}}) == {}


def test_pro_max_id():
    assert load("models").resolve_model({"id": "pironman5-pro-max"}) == ("pro_max", "automatic")


def test_optional_network_has_error_boundary():
    tree = ast.parse((ROOT / "coordinator.py").read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PironmanCoordinator")
    network = next(n for n in cls.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "_async_refresh_network")
    assert any(isinstance(n, ast.ExceptHandler) for n in ast.walk(network))


def test_diagnostics_excludes_sensitive_fields():
    source = (ROOT / "diagnostics.py").read_text()
    assert '"network_interfaces"' in source
    assert '"host":' not in source
    assert '"network_addresses":' not in source
    assert '"logs":' not in source
