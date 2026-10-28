# Changelog

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

