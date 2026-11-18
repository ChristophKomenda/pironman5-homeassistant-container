# Changelog

## [1.4.0] - 2026-11-18

### Added
- Optional per-interface IP address diagnostic sensors using `GET /api/v1.0/get-ips`.
- Read-only RGB LED count sensor when provided by the API.
- Software version and API-reported peripherals on the model diagnostic sensor.
- Home Assistant diagnostics download with allowlisted metadata only.
- Internal explicit hardware capability detection for future model-specific entities.
- Automated tests for network payload parsing, Pro Max identification, optional endpoint handling and diagnostic privacy.

### Changed
- Throttle optional IP metadata requests to at most one per 60 seconds.
- Preserve existing entity unique IDs and legacy capability handling for previously supported controls.
- Do not interrupt core monitoring when the optional network endpoint fails.

### Validation and limitations
- 76 local Python tests passed; GitHub HACS and Hassfest validation passed on PR #14.
- Pro Max support is software-ready but **not yet hardware-verified**.
- Camera, touchscreen, audio, IR and power-button events are **not** part of this release.
- RGB LED count is read-only pending verified device-specific write limits.
- v1.4.0 integration code is on `main`; check GitHub Releases for the publication status of the v1.4.0 tag.


## [1.3.3] - 2026-11-09

### Improved
- Suggested readable network transfer rates in kB/s, used RAM in GiB and CPU frequency in GHz.
- Configured sensible display precision for network, memory, CPU frequency and temperatures.
- Identified CPU frequency as a frequency sensor and exposed measurement state classes.

### Fixed
- Report PWM fan speed as rpm instead of the incorrect percentage unit.

### Compatibility
- Raw Pironman API values, existing entity unique IDs, hardware discovery and device controls remain unchanged.
- Previously configured Home Assistant display units may need manual adjustment.
- Added regression tests for the new sensor display metadata.


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

