# Contributing to Pironman 5

Thank you for helping improve the Pironman 5 / 5 Max integration for Home Assistant.

## Before contributing

- Search existing issues and pull requests to avoid duplicates.
- For substantial changes, open a feature request or discussion first.
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md).
- Report security concerns privately as described in [SECURITY.md](SECURITY.md).

## Development setup

1. Fork this repository and create a descriptive feature branch.
2. Use a Home Assistant development/test instance; avoid testing experimental code on your only production installation.
3. Copy `custom_components/pironman5` to the test instance's `custom_components` directory, then restart Home Assistant.
4. Ensure the Pironman REST API is reachable from the Home Assistant environment. Its default port is `34001`.
5. Test relevant sensors, switches, selects, numbers, and lights on available hardware.

The integration supports Home Assistant Container and deployments where the Pironman runs on a separate host. Docker's `127.0.0.1` may refer to the container, not the Raspberry Pi host.

## Code guidelines

- Follow Home Assistant conventions and use clear, maintainable Python.
- Keep polling and network operations non-blocking.
- Preserve existing entity unique IDs wherever possible.
- Handle missing hardware, unavailable API fields, and network failures gracefully.
- Avoid introducing cloud services, MQTT, or unnecessary dependencies.
- Update `strings.json` and both `translations/en.json` and `translations/de.json` when changing user-facing text.
- Update documentation when changing behavior or configuration.
- Never commit credentials, private IP addresses, or personal logs.

## Validation

Run applicable local checks and verify the existing GitHub Actions validation workflow passes. Manually test changed behavior on the hardware and deployment types available to you. Clearly state what was not tested.

## Pull requests

Keep changes focused. Describe the problem, approach, compatibility impact, and verification steps. Link related issues and include screenshots for UI changes. Maintainers may request changes before merging.

Contributions are submitted under the repository's MIT license.
