# Pironman 5 / 5 Max – Home Assistant Integration

**Monitor and control your SunFounder Pironman 5 or Pironman 5 Max directly from Home Assistant.**

A fully local, lightweight custom integration for Home Assistant, with support for **Home Assistant Container**, remote Raspberry Pi installations, and the official **Home Assistant Community Store (HACS)**.

**Local REST API · No MQTT · No cloud dependency · Configurable polling · Native Home Assistant entities**

[Installation](#installation) · [Features](#features) · [Configuration](#configuration) · [Troubleshooting](#troubleshooting) · [Releases](#releases)

---

## Official HACS Integration

**Pironman 5 is officially included in the HACS default repository!**

The integration was reviewed and accepted by the HACS maintainers through [Pull Request #12242](https://github.com/hacs/default/pull/12242).

You can install it directly through HACS without manually adding a custom repository.

**Current version: v1.1.3**

[Latest Release](https://github.com/ChristophKomenda/pironman5-homeassistant-container/releases/latest) · [Report an Issue](https://github.com/ChristophKomenda/pironman5-homeassistant-container/issues) · [Source Code](https://github.com/ChristophKomenda/pironman5-homeassistant-container)

---

## Overview

Bring your Pironman hardware into Home Assistant with system monitoring and direct control over cooling, RGB lighting, and the OLED display.

The integration communicates with the Pironman software through its local REST API.

Home Assistant and the Pironman hardware can run on the same Raspberry Pi or on separate devices connected through your local network.

### Why use this integration?

- **Fully local:** No cloud services, external accounts, or MQTT broker required.
- **Official HACS support:** Install and update directly through HACS.
- **Container-friendly:** Compatible with Home Assistant Container installations.
- **Hardware monitoring:** Track CPU, GPU, memory, NVMe storage, network activity, and cooling.
- **Fan management:** Change cooling profiles directly from Home Assistant.
- **RGB control:** Manage lighting, colors, brightness, and effects.
- **OLED control:** Configure display behavior, pages, rotation, and sleep timeout.
- **Flexible configuration:** Change the host, API port, and polling interval without reinstalling.
- **Remote access:** Connect Home Assistant to a Pironman running on another Raspberry Pi.

---

## Features

### System Monitoring

Monitor your Raspberry Pi and Pironman hardware through native Home Assistant sensor entities.

| Category | Available measurements |
|---|---|
| CPU | Temperature, usage, frequency |
| GPU | Temperature |
| Memory | Usage percentage, used memory |
| Storage | NVMe 0 usage, NVMe 1 usage |
| Network | Download speed, upload speed |
| Cooling | Fan speed, fan running status |

Sensor availability depends on the hardware and information exposed by the installed Pironman software.

### Dual NVMe Monitoring

The integration supports monitoring two NVMe drives independently.

| Drive | Device path |
|---|---|
| NVMe 0 | `/dev/nvme0n1` |
| NVMe 1 | `/dev/nvme1n1` |

The original NVMe sensor retains its existing unique ID to preserve compatibility with earlier installations.

**Note:** NVMe device paths are currently fixed. Automatic storage discovery is a potential future enhancement.

### Fan Control

Manage cooling behavior without opening the Pironman dashboard.

**Available fan profiles:**

- Always On
- Performance
- Cool
- Balanced
- Quiet

**GPIO Fan LED modes:**

- On
- Off
- Follow

Fan settings are sent to the local Pironman REST API.

### RGB Lighting

Control your Pironman's RGB lighting using Home Assistant.

**Available controls:**

- RGB power
- Brightness
- Color
- Lighting effect
- Effect speed

**Supported effects:**

| Effect | Description |
|---|---|
| Solid | Static color |
| Breathing | Pulsing brightness |
| Flow | Flowing color animation |
| Flow Reverse | Reverse flowing animation |
| Rainbow | Rainbow lighting |
| Rainbow Reverse | Reverse rainbow animation |
| Hue Cycle | Continuous color cycling |

Effects can be selected through the RGB light entity or the dedicated RGB Effect select entity.

RGB lighting can also be used in Home Assistant dashboards, scenes, and automations.

### OLED Display

Configure the Pironman OLED display from Home Assistant.

**Available controls:**

- Enable or disable the display
- OLED Always On
- Sleep timeout
- Display rotation
- Primary OLED page

**Supported pages:**

- Mix
- Performance
- IPs
- Disk

OLED functionality depends on compatible Pironman hardware and API support.

### OLED Always On

The **OLED Always On** switch allows the display to remain active without an automatic sleep timeout.

| State | Behavior |
|---|---|
| On | Sets the OLED sleep timeout to `0` |
| Off | Restores the previously observed positive timeout |

The feature uses the existing Pironman REST API.

**How to use it:**

1. Open the Pironman device in Home Assistant.
2. Locate the **OLED Always On** switch.
3. Enable it to disable automatic sleep.
4. Disable it to restore the previous timeout.

**Important behavior:**

- The main OLED enable switch must remain enabled.
- The Always On state is derived from the timeout reported by the API.
- A timeout of `0` means no automatic sleep in supported Pironman software.
- The previous timeout is remembered only during the current Home Assistant session.
- If the previous value is unavailable, the integration uses a fallback of **10 seconds**.
- Continuous OLED operation may increase display wear or burn-in risk.

### OLED Sleep Timeout

The OLED Sleep Timeout entity provides direct control over the display's automatic sleep behavior.

| Value | Behavior |
|---|---|
| `0` seconds | No automatic sleep |
| `1–3600` seconds | Automatic sleep after the selected timeout |

The Always On switch provides a convenient alternative to manually changing the timeout.

---

## Requirements

| Component | Requirement |
|---|---|
| Hardware | SunFounder Pironman 5 or Pironman 5 Max |
| Home Assistant | Version 2024.1.0 or newer |
| Pironman software | Running with its local REST API available |
| Network | Home Assistant must be able to reach the Pironman API |
| Default API port | `34001` |
| Installation | HACS or manual custom integration |

The Pironman software must be installed and running on the Raspberry Pi.

The integration communicates with the local API and does not replace the underlying Pironman software.

---

## Installation

### Option A — HACS (Recommended)

Pironman 5 is available through the official HACS repository.

1. Open **HACS** in Home Assistant.
2. Search for **Pironman 5**.
3. Open the integration page.
4. Select **Download**.
5. Follow the installation prompts.
6. Restart Home Assistant when prompted.

After installation, continue with [Configuration](#configuration).

**Previously installed as a custom repository?**

If you added this repository manually before its official HACS inclusion, you can continue using the existing integration. Avoid creating duplicate installations; review your HACS repository settings if needed.

### Option B — Manual Installation

1. Download the [latest release](https://github.com/ChristophKomenda/pironman5-homeassistant-container/releases/latest).
2. Extract the repository.
3. Copy the `custom_components/pironman5` directory into your Home Assistant configuration directory.
4. Restart Home Assistant.

Your installation should contain:

```text
config/
└── custom_components/
    └── pironman5/
        ├── __init__.py
        ├── config_flow.py
        ├── coordinator.py
        ├── manifest.json
        ├── strings.json
        ├── translations/
        │   ├── en.json
        │   └── de.json
        └── ...
```

For Home Assistant Container, the configuration directory is typically mounted as `/config` inside the container.

---

## Configuration

### Initial Setup

After installing and restarting Home Assistant:

1. Navigate to **Settings → Devices & Services**.
2. Click **Add Integration**.
3. Search for **Pironman 5**.
4. Enter the IP address or hostname of the Raspberry Pi running the Pironman API.
5. Enter the API port, normally `34001`.
6. Complete the setup.

Home Assistant will connect to the local Pironman API and create the supported entities.

### Connection Settings

Connection settings can be changed without removing and reinstalling the integration.

Navigate to:

**Settings → Devices & Services → Pironman 5 → Configure**

| Setting | Description |
|---|---|
| Host / IP address | Address of the Raspberry Pi running Pironman |
| API port | Default: `34001` |
| Polling interval | Configurable between 5 and 60 seconds |

The integration reloads automatically after saving configuration changes.

A polling interval of **10 seconds** is a reasonable starting point for many installations.

Shorter intervals provide more frequent updates but increase API requests.

Longer intervals reduce polling activity.

---

## Supported Deployment Scenarios

### Home Assistant on the Same Raspberry Pi

Home Assistant and the Pironman REST API can run on the same Raspberry Pi.

When using Home Assistant Container, configure the address that is reachable from inside the container.

Depending on the Docker network configuration, `127.0.0.1` may refer to the container itself rather than the Raspberry Pi host.

Using the Raspberry Pi's LAN IP address is often the simplest option.

### Home Assistant on a Separate Device

The integration also supports installations where Home Assistant runs on a different Raspberry Pi or home server.

```text
Raspberry Pi 5
SunFounder Pironman 5 / 5 Max
│
├── Pironman hardware
├── Pironman software
└── Local REST API
    Port 34001
         │
         │ Local network
         │
         ▼
Home Assistant Host
│
├── Home Assistant
│   or Home Assistant Container
│
└── Pironman 5 Integration
```

Configure the integration with the network address of the Raspberry Pi hosting the Pironman API.

Ensure that the configured API port is reachable from Home Assistant.

### Network and Security

The Pironman API is intended for communication within a trusted local network.

For security:

- Keep the API accessible only to trusted devices.
- Avoid exposing port `34001` directly to the internet.
- Use appropriate firewall rules and network segmentation.
- Keep the Pironman software and Home Assistant updated.

---

## Updating

### HACS Updates

For installations managed through HACS:

1. Open HACS.
2. Check for an available Pironman 5 update.
3. Download the new version.
4. Restart Home Assistant when required.
5. Verify that the entities are available.

Existing configuration entries should normally remain intact during updates.

### Manual Updates

For manual installations:

1. Download the latest release.
2. Replace the files in `custom_components/pironman5`.
3. Restart Home Assistant.
4. Verify the integration under **Devices & Services**.

Avoid mixing files from different releases.

---

## Troubleshooting

### Integration Cannot Connect

Check whether the Pironman REST API is reachable.

From the Home Assistant host, run:

```bash
curl http://PIRONMAN_IP:34001/api/v1.0/get-data
```

Replace `PIRONMAN_IP` with the actual IP address of your Pironman device.

If the request fails:

- Verify the IP address and port.
- Confirm that the Pironman software is running.
- Check network connectivity.
- Review firewall settings.
- For Docker installations, verify connectivity from the container network.

### Sensors Are Unavailable

- Verify that the Pironman API returns valid data.
- Check the configured host and port.
- Confirm the relevant hardware is installed.
- Review the Home Assistant logs.
- Restart the integration if necessary.

### Second NVMe Sensor Is Unavailable

The second NVMe sensor expects data for `/dev/nvme1n1`.

If that device is missing or the Pironman API does not expose its usage, the sensor may be unavailable.

### OLED Always On Switch Is Missing

1. Confirm the latest integration version is installed.
2. Restart Home Assistant.
3. Open **Settings → Devices & Services → Pironman 5**.
4. Inspect the device's available entities.
5. Check the Home Assistant logs.

The switch uses the unique ID suffix `_oled_always_on`.

### OLED Always On Is Unavailable

The switch requires the `oled_sleep_timeout` setting from the Pironman API.

Check:

```bash
curl http://PIRONMAN_IP:34001/api/v1.0/get-config
```

Verify that the response includes `oled_sleep_timeout`.

If it is missing, review your installed Pironman software version and API compatibility.

### OLED Still Turns Off

- Verify that the main OLED switch is enabled.
- Check that the API reports a sleep timeout of `0`.
- Confirm that the Pironman software supports disabling automatic sleep.
- Check whether another service changes the OLED configuration.
- Review the Home Assistant and Pironman logs.

OLED Always On disables the automatic sleep timer. It does not prevent shutdown or manual display deactivation.

### Previous OLED Timeout Is Not Restored

The previous positive timeout is stored only in memory during the current Home Assistant session.

If Home Assistant or the integration restarts, that value may be lost.

In that case, disabling Always On restores the fallback of **10 seconds**.

You can manually configure your preferred timeout again.

### Configuration Changes Do Not Apply

Save the updated settings and allow Home Assistant to reload the integration.

If necessary, restart Home Assistant and review the logs.

---

## Releases

### v1.1.3 — HACS Maintenance Release

- Updated documentation and issue tracker URLs to the current repository.
- Updated integration version to `1.1.3`.
- Maintenance release following official HACS inclusion.
- No intended functional changes.

### v1.1.2 — English Translation Fix

- Added `translations/en.json`.
- Ensured English fallback translations are available for the configuration flow.
- Addressed feedback from the HACS review process.

### v1.1.x — Configuration and Monitoring Improvements

- Configurable host and API port.
- Configurable polling interval.
- Independent NVMe 0 and NVMe 1 monitoring.
- Preservation of the original NVMe sensor's unique ID.

### Earlier Enhancements

- OLED Always On switch.
- OLED sleep timeout restoration behavior.
- Existing hardware monitoring and control capabilities.

For the complete release history, visit [GitHub Releases](https://github.com/ChristophKomenda/pironman5-homeassistant-container/releases).

---

## Roadmap

Potential future improvements include:

- Automatic NVMe and USB storage discovery
- Additional system and hardware monitoring entities
- More diagnostic information
- Persistent storage of the previous OLED timeout
- Additional dashboard examples
- More Home Assistant automation examples
- Further localization improvements

These are potential enhancements rather than committed release features.

Suggestions and contributions are welcome.

---

## Contributing

Contributions, bug reports, translations, and feature suggestions are appreciated.

If you discover a problem or would like to propose an improvement:

1. Check the existing GitHub issues.
2. Open a new issue with a clear description.
3. Include relevant hardware and software versions.
4. Provide logs or reproduction steps when appropriate.
5. Submit a pull request if you would like to contribute code.

**Useful links:**

- [Issue Tracker](https://github.com/ChristophKomenda/pironman5-homeassistant-container/issues)
- [Pull Requests](https://github.com/ChristophKomenda/pironman5-homeassistant-container/pulls)
- [Latest Release](https://github.com/ChristophKomenda/pironman5-homeassistant-container/releases/latest)
- [GitHub Actions](https://github.com/ChristophKomenda/pironman5-homeassistant-container/actions)

Please avoid posting passwords, access tokens, or other sensitive information in issues or logs.

---

## License

See the [LICENSE](LICENSE) file for the applicable license terms.

---

## Acknowledgements

Thanks to [SunFounder](https://www.sunfounder.com/) for the Pironman hardware and software ecosystem.

Special thanks to the Home Assistant community and the HACS maintainers for their work supporting custom integrations.

The integration was officially accepted into HACS through [hacs/default#12242](https://github.com/hacs/default/pull/12242).

---

## Maintainer

Developed and maintained by [Christoph Komenda](https://github.com/ChristophKomenda).

**Built for the SunFounder Pironman community.**

If you find this integration useful, consider starring the repository on GitHub!
