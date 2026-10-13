# Pironman 5 / 5 Max – Home Assistant Integration

**Monitor and control your SunFounder Pironman 5 or Pironman 5 Max directly from Home Assistant.**

A lightweight, fully local custom integration for Home Assistant, including **Home Assistant Container** installations.

**No MQTT · No cloud dependency · Local REST API · Configurable polling**

[Installation](#installation) · [Features](#features) · [Configuration](#configuration) · [Troubleshooting](#troubleshooting)

---

## Overview

Bring your Pironman hardware into Home Assistant with real-time system monitoring and direct control over fans, RGB lighting, and the OLED display.

Whether Home Assistant runs on the same Raspberry Pi or on a separate device, the integration communicates directly with the Pironman REST API over your local network.

### Why use this integration?

- **Fully local:** No cloud account or MQTT broker required.
- **Container-friendly:** Designed to work with Home Assistant Container.
- **Hardware control:** Manage fan settings, RGB lighting, and OLED options.
- **System monitoring:** Track temperatures, CPU, memory, network activity, and NVMe usage.
- **Flexible setup:** Change the device IP, API port, and polling interval directly in Home Assistant.
- **Remote connectivity:** Run Home Assistant on a separate Raspberry Pi or server.

> **HACS submission pending**
>
> The integration has been submitted to the official HACS default repository and is awaiting review.
>
> [View HACS Pull Request #10913](https://github.com/hacs/default/pull/10913)

## Features

### System Monitoring

Monitor your Pironman hardware through native Home Assistant entities.

| Category | Available sensors |
|---|---|
| CPU | Temperature, usage, frequency |
| GPU | Temperature |
| Memory | Usage percentage, used memory |
| Storage | NVMe 0 usage, NVMe 1 usage |
| Network | Download speed, upload speed |
| Cooling | Fan speed, fan running status |

**Dual NVMe monitoring (v1.1.0)**

Monitor two NVMe drives independently:

- NVMe 0: `/dev/nvme0n1`
- NVMe 1: `/dev/nvme1n1`

The existing NVMe sensor retains its unique ID to maintain compatibility with previous installations.

> NVMe device paths are currently fixed. Automatic discovery of additional NVMe and USB drives is planned as a potential future improvement.

### Fan Control

Adjust your Pironman's cooling behavior directly from Home Assistant.

**Available fan modes**

- Always On
- Performance
- Cool
- Balanced
- Quiet

**GPIO Fan LED**

- On
- Off
- Follow

Fan settings are managed through the local Pironman REST API.

### RGB Lighting

Control your Pironman's RGB lighting without leaving Home Assistant.

**Controls**

- RGB power on/off
- Brightness
- Color
- Effect selection
- Effect speed

**Available effects**

| Effect | Description |
|---|---|
| Solid | Static color |
| Breathing | Pulsing brightness |
| Flow | Flowing color animation |
| Flow Reverse | Reverse flow animation |
| Rainbow | Rainbow animation |
| Rainbow Reverse | Reverse rainbow animation |
| Hue Cycle | Continuous color cycling |

RGB effects can be selected through the RGB Light entity or the dedicated **RGB Effect** select entity.

This makes it easy to include lighting effects in dashboards, scenes, and automations.

### OLED Display

Control the **Pironman 5 Max OLED display** directly from Home Assistant.

Supported options:

- Enable or disable the display
- Rotate the display (0° / 180°)
- Configure the sleep timeout
- Select the primary OLED page
- Synchronize settings with the Pironman API

**Available OLED pages:** Mix, Performance, IPs, Disk.

## Requirements

| Component | Requirement |
|---|---|
| Hardware | SunFounder Pironman 5 or Pironman 5 Max |
| Home Assistant | Home Assistant with support for custom integrations |
| Pironman software | Running with the local REST API enabled |
| Network | Home Assistant must be able to reach the Pironman API |
| Default API port | `34001` |

The Pironman REST API must be running and accessible from your Home Assistant installation.

## Installation

### Option A — HACS (Recommended)

Until the integration is available in the default HACS repository, install it as a custom repository.

1. Open **HACS** in Home Assistant.
2. Open the menu and select **Custom repositories**.
3. Add the following repository URL:

   `https://github.com/ChristophKomenda/pironman5-homeassistant-container`

4. Select **Integration** as the repository category.
5. Add the repository and install the integration.
6. Restart Home Assistant.

Once the HACS submission is approved, the integration may become available through the default HACS catalog.

### Option B — Manual Installation

1. Download or clone this repository.
2. Copy the `custom_components/pironman5` directory into your Home Assistant configuration directory.
3. Ensure the directory structure looks like this:

   ```text
   config/
   └── custom_components/
       └── pironman5/
           ├── __init__.py
           ├── config_flow.py
           ├── coordinator.py
           ├── manifest.json
           └── ...
   ```

4. Restart Home Assistant.

For Home Assistant Container, the configuration directory is typically mounted as `/config` inside the container.

## Configuration

### First-Time Setup

After installation:

1. Open **Settings → Devices & Services**.
2. Select **Add Integration**.
3. Search for **Pironman 5**.
4. Enter the IP address or hostname of the Raspberry Pi running the Pironman API.
5. Enter the API port (default: `34001`).
6. Complete the setup.

Home Assistant will connect to the Pironman REST API and create the supported entities.

### Change Connection Settings (v1.1.0)

You can update the connection without removing or reinstalling the integration.

Navigate to:

**Settings → Devices & Services → Pironman 5 → Configure**

| Setting | Description |
|---|---|
| Host / IP address | Pironman device IP or hostname |
| API port | Default: `34001` |
| Polling interval | 5–60 seconds |

The integration reloads automatically after configuration changes.

A polling interval of **10 seconds** is a reasonable starting point for many installations.

## Supported Setups

### Same Raspberry Pi

Home Assistant and the Pironman REST API run on the same device.

Configure the integration using the API address reachable from Home Assistant.

### Separate Raspberry Pis or Servers

Home Assistant can run on a different device from the Pironman hardware.

```text
Raspberry Pi 5 — Pironman 5 Max
│
├── Pironman hardware
├── Pironman REST API
└── Port 34001
         │
         │ Local network
         │
         ▼
Raspberry Pi / Home Server
│
├── Home Assistant Container
└── Pironman 5 Integration
```

For this setup, use the network IP address of the Raspberry Pi with the Pironman hardware, not `127.0.0.1`.

Ensure the API port is accessible from the Home Assistant host.

## Upgrading

Existing installations can be updated without removing their configuration entries.

1. Update the integration through HACS or replace the integration files manually.
2. Restart Home Assistant.
3. Open the Pironman integration under **Devices & Services**.
4. Use **Configure** to review connection settings.
5. Check that your sensors and controls are available.

**Upgrading to v1.1.0**

- Adds configurable host, API port, and polling interval.
- Adds separate NVMe 0 and NVMe 1 usage sensors.
- Preserves the existing NVMe sensor's unique ID.

## Troubleshooting

### Integration Cannot Connect

Verify that the Pironman REST API is running and reachable.

From the Home Assistant host, test:

```bash
curl http://PIRONMAN_IP:34001/api/v1.0/get-data
```

Replace `PIRONMAN_IP` with the actual IP address of your Pironman device.

If the request fails:

- Confirm the IP address and API port.
- Verify the Pironman service is running.
- Check network connectivity and firewall rules.
- For Docker installations, ensure the container can reach the Pironman device.

### Sensors Are Unavailable

- Check that the API returns data.
- Confirm the integration is configured with the correct host.
- Review the Home Assistant logs.
- Verify that the expected hardware is installed.

### Second NVMe Sensor Has No Value

The second NVMe sensor reads data from `/dev/nvme1n1`.

If the Pironman API does not expose that device, the sensor may be unavailable.

### Configuration Changes Do Not Apply

Save the integration options and allow Home Assistant to reload the integration.

If the problem persists, restart Home Assistant and check the logs.

## Roadmap

Potential future improvements include:

- Automatic NVMe and USB storage discovery
- Additional hardware monitoring entities
- Expanded diagnostics and troubleshooting
- Further dashboard and automation examples

Feature requests and contributions are welcome.

## Contributing

Contributions, bug reports, and feature suggestions are appreciated.

If you discover an issue or have an idea for improvement, please open an issue or pull request on GitHub.

[Report an issue](https://github.com/ChristophKomenda/pironman5-homeassistant-container/issues)

## License

See the repository's license file for licensing information.

---

**Built for the SunFounder Pironman community.**

Developed and maintained by [Christoph Komenda](https://github.com/ChristophKomenda).
