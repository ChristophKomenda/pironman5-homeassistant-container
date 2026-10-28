"""Basic structural safety checks for storage tracking."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components/pironman5"


def test_tracking_checks_api_success():
    source = (COMPONENT / "coordinator.py").read_text()
    assert "not self.last_update_success" in source
    assert 'key.startswith("disk_/dev/")' in source


def test_tracking_handles_errors():
    source = (COMPONENT / "sensor.py").read_text()
    assert "Pironman storage absence tracking failed" in source
    assert "except asyncio.CancelledError:" in source


def test_tracking_stops_on_unload():
    source = (COMPONENT / "sensor.py").read_text()
    assert "def stop_storage_tracking():" in source
    assert "tracking_task.cancel()" in source
    assert "entry.async_on_unload(stop_storage_tracking)" in source
