# Pironman 5 Home Assistant Container

A local Home Assistant custom integration for the **SunFounder Pironman 5 and Pironman 5 Max**.

The integration communicates directly with the local Pironman REST API. **No MQTT broker, cloud service or additional software is required.**

This project provides a local workaround for **Home Assistant Container** installations, where the official SunFounder Home Assistant integration currently does not support the required functionality.


> 🧩 **HACS submission pending**
> This integration has been submitted to the official HACS default repository and is currently awaiting review.
>
> **[View HACS Pull Request #10913 →](https://github.com/hacs/default/pull/10913)**


## What's New in v1.1.0

### Configurable Connection Settings

Update the Pironman host/IP address, API port, and polling interval
directly in Home Assistant without removing the integration.

Navigate to **Settings → Devices & Services → Pironman 5 → Configure**.

| Setting | Description |
| --- | --- |
| Host / IP | Address of the Pironman device |
| API port | Default: `34001` |
| Polling interval | Configurable from 5 to 60 seconds |

Configuration changes automatically reload the integration.

### Dual NVMe Monitoring

The integration provides separate usage sensors for:

- **NVMe 0 Usage** — `/dev/nvme0n1`
- **NVMe 1 Usage** — `/dev/nvme1n1`

The original NVMe sensor retains its unique ID to preserve
compatibility with existing Home Assistant installations.

Automatic discovery of additional NVMe or USB drives is not yet supported.

### Remote Home Assistant Support

Home Assistant Container can run on a separate Raspberry Pi.

The integration communicates over the local network with the
Pironman REST API on the device hosting the Pironman hardware.

Make sure the API port is reachable from Home Assistant.

### Upgrading from v1.0.3

Update the integration and restart Home Assistant.

Existing configuration entries do not need to be removed.
Use the new **Configure** option to adjust the connection settings.

## Features

### Monitoring

- CPU temperature
- GPU temperature
- CPU usage
- CPU frequency
- Memory usage
- Memory used
- NVMe 0 and NVMe 1 usage (separate sensors)
- Network download speed
- Network upload speed
- Fan speed
- Fan running status

### Fan Control

- Fan mode
  - Always On
  - Performance
  - Cool
  - Balanced
  - Quiet
- GPIO fan LED
  - On
  - Off
  - Follow

The GPIO fan LED can be controlled directly through Home Assistant using the local Pironman REST API.

### RGB Control

- RGB on/off
- RGB brightness
- RGB color
- RGB effect selection
  - Solid
  - Breathing
  - Flow
  - Flow Reverse
  - Rainbow
  - Rainbow Reverse
  - Hue Cycle
- RGB effect speed

The RGB effects can be controlled through the RGB Light entity or through a dedicated **RGB Effect** select entity.

The dedicated RGB Effect selector makes it easy to use RGB effects in Home Assistant dashboards and automations.

### OLED

The integration provides local control of the **Pironman 5 Max OLED display**.

Currently supported:

- Enable / disable OLED display
- OLED rotation (0° / 180°)
- OLED sleep timeout
- OLED page selection
  - Mix
  - Performance
  - IPs
  - Disk
- Local control through Home Assistant
- Automatic state synchronization with the Pironman API

The OLED page selector controls the primary OLED page directly from Home Assistant.

## Requirements

- Home Assistant
- SunFounder Pironman 5 or Pironman 5 Max
- Pironman software with the local REST API
- Pironman Dashboard/API running on port `34001`

The integration communicates with the local Pironman API on port `34001` by default.

## Installation

### HACS

Install the integration through HACS.

If the repository is not yet available in the default HACS store, add this repository as a custom repository in HACS:

```text
https://github.com/ChristophKomenda/pironman5-homeassistant-container
