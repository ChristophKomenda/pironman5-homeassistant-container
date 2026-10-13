# Pironman 5 Home Assistant Container

A local Home Assistant custom integration for the **SunFounder Pironman 5 and Pironman 5 Max**.

The integration communicates directly with the local Pironman REST API. **No MQTT broker, cloud service or additional software is required.**

This project provides a local workaround for **Home Assistant Container** installations, where the official SunFounder Home Assistant integration currently does not support the required functionality.


> 🧩 **HACS submission pending**
> This integration has been submitted to the official HACS default repository and is currently awaiting review.
>
> **[View HACS Pull Request #10913 →](https://github.com/hacs/default/pull/10913)**


## Features

### Monitoring

- CPU temperature
- GPU temperature
- CPU usage
- CPU frequency
- Memory usage
- Memory used
- NVMe usage
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
