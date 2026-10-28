# Pironman 5 Family — Home Assistant Integration

**Monitor and control compatible SunFounder Pironman 5 family hardware directly from Home Assistant.**

A fully local custom integration for Home Assistant Container, Home Assistant OS, and other supported Home Assistant installations.

The integration communicates with the Pironman software through its local REST API — **no cloud account, MQTT broker, or additional Home Assistant add-on required.**

[![Latest Release](https://img.shields.io/github/v/release/ChristophKomenda/pironman5-homeassistant-container?label=release)](https://github.com/ChristophKomenda/pironman5-homeassistant-container/releases/latest)
[![HACS Default](https://img.shields.io/badge/HACS-Default-41BDF5)](https://github.com/hacs/default/pull/12242)
[![License: MIT](https://img.shields.io/github/license/ChristophKomenda/pironman5-homeassistant-container)](https://github.com/ChristophKomenda/pironman5-homeassistant-container/blob/main/LICENSE)

**Local REST API · Automatic Model Detection · Hardware Monitoring · Fan Control · RGB · OLED**

> **Official HACS default repository integration**
>
> Pironman 5 has been reviewed and accepted into the HACS default repository. You can install it directly through HACS without adding a custom repository.

## Features

### System Monitoring

Monitor your Raspberry Pi hardware using native Home Assistant entities.

| Category | Available Sensors |
|---|---|
| CPU | Temperature, usage, frequency |
| GPU | Temperature |
| Memory | Usage percentage, used memory |
| Storage | NVMe 0 and NVMe 1 usage |
| Network | Download and upload speed |
| Cooling | Fan speed and running status |
| Device | Detected Pironman model |

Sensor availability depends on the connected hardware and the information exposed by the installed Pironman API.

### Fan Control

Manage supported cooling settings directly from Home Assistant.

Available fan profiles:

- Always On
- Performance
- Cool
- Balanced
- Quiet

Additional GPIO fan LED settings may be available depending on the connected hardware.

### RGB Lighting

Control compatible Pironman RGB lighting using native Home Assistant light entities.

Supported functions:

- RGB on/off
- Brightness adjustment
- RGB color selection
- Lighting effects
- Effect speed

Available effects:

- Solid
- Breathing
- Flow / Flow Reverse
- Rainbow / Rainbow Reverse
- Hue Cycle

RGB lighting can also be included in Home Assistant dashboards, scenes, and automations.

### OLED Display

Manage compatible Pironman OLED displays directly from Home Assistant.

Supported functions:

- Enable or disable the display
- Display rotation
- Sleep timeout
- Always On mode
- Primary display page selection
- State synchronization with the local API

Available display pages depend on the hardware and upstream API implementation.

**OLED Always On**

The Always On switch disables automatic display sleep by setting the sleep timeout to `0`.

When disabled, the integration attempts to restore the previously observed positive timeout.

**Note:** The previous timeout is currently remembered only during the active Home Assistant session. After a restart, a fallback of 10 seconds may be used.

Continuous OLED operation may increase display wear or burn-in risk.

## Supported Hardware

Version **1.3.0** adds dynamic NVMe and USB storage discovery, hot-plug support, and availability handling for disconnected drives. It builds on the automatic model detection and capability-aware entity setup introduced in v1.2.0.

| Pironman Model | Implementation | Hardware Verification |
|---|---|---|
| Pironman 5 | Model detection and capability handling | Not verified |
| Pironman 5 Mini | Model detection and capability handling | Not verified |
| Pironman 5 Max | Model detection and capability handling | Maintainer-tested |
| Pironman 5 Pro Max | Model detection and capability handling | Not verified |

The integration attempts to detect the connected model automatically through the Pironman REST API.

If automatic detection is unavailable, users can select their model manually.

When the API reports supported peripherals, the integration uses this information to avoid exposing unsupported hardware controls.

**Important:** Model recognition does not guarantee full hardware compatibility. Untested models may expose different API capabilities.

The Pironman 5 Max has been tested with Home Assistant Container 2026.10.1 and Pironman API 1.3.20. Individual controls have not all been independently revalidated for v1.2.0.

For detailed compatibility information and community testing instructions, see:

[Hardware Compatibility & Testing](https://github.com/ChristophKomenda/pironman5-homeassistant-container/blob/main/docs/hardware-testing.md)

## Requirements

- Home Assistant 2024.1.0 or newer
- Compatible Raspberry Pi with Pironman hardware
- Installed and running SunFounder Pironman software
- Accessible local Pironman REST API
- Network connectivity between Home Assistant and the Pironman device

The default API port is `34001`.

The integration requires the upstream Pironman software to operate the hardware. It does not replace the official SunFounder software.

## Installation

### Option A — HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Search for **Pironman 5**.
3. Open the integration and select **Download**.
4. Complete the installation.
5. Restart Home Assistant when prompted.
6. Navigate to **Settings → Devices & Services**.
7. Select **Add Integration**.
8. Search for **Pironman 5**.
9. Enter the Raspberry Pi hostname or IP address and API port.

No custom HACS repository URL is required.

### Option B — Manual Installation

Download the latest release:

[GitHub Releases](https://github.com/ChristophKomenda/pironman5-homeassistant-container/releases/latest)

Copy the `pironman5` integration directory into:

```text
/config/custom_components/pironman5/
```

Restart Home Assistant and add the integration through **Settings → Devices & Services**.

## Configuration

The integration supports configuration through the Home Assistant UI.

| Setting | Description |
|---|---|
| Host / IP | Address of the Raspberry Pi running Pironman |
| API Port | Default: `34001` |
| Polling Interval | Configurable from 5 to 60 seconds |
| Pironman Model | Automatic detection or manual selection |

A polling interval of 10 seconds is a reasonable starting point.

Configuration settings can be changed under:

**Settings → Devices & Services → Pironman 5 → Configure**

Changes automatically trigger an integration reload.

### Home Assistant Container

If Home Assistant runs inside Docker, remember that `127.0.0.1` may refer to the container itself rather than the Raspberry Pi host.

Use a hostname or IP address that is reachable from the Home Assistant container.

For installations using host networking, `127.0.0.1` may work when the Pironman service runs on the same host.

### Remote Home Assistant Installation

Home Assistant and Pironman do not need to run on the same device.

You can monitor and control a compatible Pironman device from another Home Assistant installation on your trusted local network.

## Local REST API

The integration communicates with the local Pironman API:

```text
http://PIRONMAN_IP:34001/api/v1.0/
```

Example API endpoints:

| Endpoint | Purpose |
|---|---|
| `/get-device-info` | Device identification and capabilities |
| `/get-data` | System monitoring values |
| `/get-config` | Hardware configuration |

Control commands are sent through the appropriate API endpoints.

No cloud connection is required.

**Security:** Do not expose port `34001` directly to the public internet. Restrict API access to trusted local devices.

## Troubleshooting

### Integration Cannot Connect

Verify that the Pironman software is running and that its REST API is reachable.

Test the API:

```bash
curl http://PIRONMAN_IP:34001/api/v1.0/get-data
```

A successful response should include:

```json
{
  "status": true
}
```

Check:

- Correct hostname or IP address
- Correct API port
- Running Pironman service
- Firewall configuration
- Docker network connectivity

### Automatic Model Detection Fails

The installed Pironman API may not provide sufficient device metadata.

Open the integration configuration and select the correct model manually.

Manual model selection does not enable hardware capabilities that the API does not support.

### Sensors Are Unavailable

Verify that the required hardware is installed and that the Pironman API provides the corresponding values.

NVMe sensors currently use fixed device paths:

```text
/dev/nvme0n1
/dev/nvme1n1
```

If a drive is absent or its usage information is not exposed, its sensor may be unavailable.

### RGB or Fan Controls Do Not Work

Verify that the connected hardware supports the requested feature.

Check the upstream Pironman configuration and confirm that the corresponding API functions are available.

### OLED Always On Is Unavailable

Verify that the API provides the `oled_sleep_timeout` setting.

Test:

```bash
curl http://PIRONMAN_IP:34001/api/v1.0/get-config
```

The OLED Always On feature requires compatible hardware and upstream API support.

## Documentation & Support

| Resource | Link |
|---|---|
| Main Documentation | [Project README](https://github.com/ChristophKomenda/pironman5-homeassistant-container) |
| Hardware Compatibility | [Testing Matrix](https://github.com/ChristophKomenda/pironman5-homeassistant-container/blob/main/docs/hardware-testing.md) |
| Latest Releases | [GitHub Releases](https://github.com/ChristophKomenda/pironman5-homeassistant-container/releases) |
| Bug Reports | [GitHub Issues](https://github.com/ChristophKomenda/pironman5-homeassistant-container/issues/new/choose) |
| Contributions | [Contributing Guidelines](https://github.com/ChristophKomenda/pironman5-homeassistant-container/blob/main/CONTRIBUTING.md) |
| Security | [Security Policy](https://github.com/ChristophKomenda/pironman5-homeassistant-container/blob/main/SECURITY.md) |

Community testing and contributions are welcome, particularly for Pironman variants that have not yet been verified on physical hardware.

## License

This project is released under the [MIT License](https://github.com/ChristophKomenda/pironman5-homeassistant-container/blob/main/LICENSE).

## Maintainer

Developed and maintained by [Christoph Komenda](https://github.com/ChristophKomenda).

This is a community-maintained integration and is not official SunFounder software.

**Built for the SunFounder Pironman community.**

If this integration helps you, consider starring the repository on GitHub.
