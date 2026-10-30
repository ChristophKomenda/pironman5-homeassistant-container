# Changelog

## [1.3.2] - 2026-10-30

### Added
- Support for multiple Pironman 5 devices in one Home Assistant instance.
- Raspberry Pi microSD storage monitoring (`/dev/mmcblk0`).
- Regression tests for multi-device configuration and SD card discovery.

### Changed
- Removed the single-config-entry restriction.
- Extended dynamic storage discovery to include `mmcblk` devices.

### Verified
- 66 automated tests passed during development.
- Successfully tested two Pironman 5 Max devices simultaneously.
- Confirmed independent hardware sensors and microSD monitoring.

## [1.3.1] - 2026-10-28

### Added
- Persistent storage absence tracking infrastructure with a 24-hour threshold.
- Non-destructive storage cleanup dry-run logging.
- Guarded entity registry cleanup utilities with deletion disabled by default.
- Automated regression tests for tracking, registry safety, and lifecycle handling.

### Changed
- Treat ambiguous storage API values (`None`, `0`, or missing data) as unknown.
- Improve storage tracking task serialization and integration unload handling.

### Safety
- Automatic entity removal remains disabled.
- Physical drive removal cannot yet be reliably confirmed through the current API.
- Existing entity unique IDs remain unchanged.

## [1.3.0] - 2026-10-28

### Added
- Dynamic NVMe and USB storage discovery.
- Hot-plug sensor registration without a Home Assistant restart.
- Availability handling for disconnected storage devices.
- Nine storage discovery regression tests.

### Changed
- Centralized storage discovery logic in the coordinator.
- Preserved existing NVMe entity identifiers.

### Known limitations
- Linux device paths may change after reconnecting a drive.
- Stable physical disk identification is not yet supported.

