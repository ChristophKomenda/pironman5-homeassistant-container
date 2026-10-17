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
- **Always-on OLED:** Keep the OLED display active without a sleep timeout.

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

Control the Pironman OLED display directly from Home Assistant.

**Supported options**

- Enable or disable the OLED display.
- Keep the OLED permanently active with **OLED Always On**.
- Configure the OLED sleep timeout.
- Rotate the display (0° / 180°).
- Select the primary OLED page.
- Synchronize settings with the local Pironman API.

**Available OLED pages:** Mix, Performance, IPs, Disk.

#### OLED Always On

The **OLED Always On** switch allows the display to remain active indefinitely, bypassing the normal sleep timer.

This is particularly useful when using the Pironman as a continuously visible system-monitoring display.

| Switch state | Behavior |
|---|---|
| On | Disables automatic OLED sleep by setting the timeout to `0` |
| Off | Restores the previously configured sleep timeout |

**How it works**

1. Open the Pironman device in Home Assistant.
2. Find the **OLED Always On** switch.
3. Turn it on to disable automatic sleep.
4. Turn it off to restore the previous sleep timeout.

The switch uses the existing SunFounder REST API endpoint and does not require an additional service or MQTT broker.

**Timeout restoration**

When Always On is enabled, the integration remembers the last positive sleep timeout observed during the current Home Assistant session.

When disabled, it restores that value.

If the previous timeout is unavailable, the integration uses a fallback of **10 seconds**.

**Important notes**

- Always On does not override the main OLED enable/disable switch. The OLED must still be enabled.
- The Always On state is derived from the timeout reported by the Pironman API.
- The timeout value `0` represents unlimited runtime in the supported SunFounder OLED software.
- The previous timeout is remembered in memory, not stored persistently by Home Assistant.
- After an integration restart, the previous timeout may no longer be available.
- Continuous OLED operation may increase the risk of display wear or burn-in.

#### OLED Sleep Timeout

The existing **OLED Sleep Timeout** number entity allows you to configure the automatic sleep delay.

| Value | Behavior |
|---|---|
| `0` seconds | No automatic sleep |
| `1–3600` seconds | Automatic sleep after the configured timeout |

Setting the timeout to `0` directly has the same sleep-disabling effect as enabling the Always On switch.

The Always On switch provides a more convenient way to toggle this behavior while restoring the previous timeout when possible.

## Requirements

| Component | Requirement |
|---|---|
| Hardware | SunFounder Pironman 5 or Pironman 5 Max |
| Home Assistant | Home Assistant with support for custom integrations |
| Pironman software | Running with the local REST API enabled |
| Network | Home Assistant must be able to reach the Pironman API |
| Default API port | `34001` |

The Pironman REST API must be running and accessible from your Home Assistant installation.

The OLED controls require compatible Pironman hardware and firmware exposing the corresponding API settings.

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
           ├── oled.py
           ├── switch.py
           ├── number.py
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

**OLED Always On enhancement**

- Adds a dedicated **OLED Always On** switch.
- Disables automatic OLED sleep using the existing API.
- Restores the previously observed positive timeout when Always On is disabled.
- Uses a 10-second fallback when no previous timeout is known.
- Preserves the existing OLED enable/disable and timeout entities.

After updating, restart Home Assistant to register the new switch entity.

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

### OLED Always On Switch Is Missing

If the switch does not appear after updating:

1. Confirm the latest integration files are installed.
2. Restart Home Assistant.
3. Open **Settings → Devices & Services → Pironman 5**.
4. Check the device's available entities.
5. Verify that `switch.py` contains the `PironmanOLEDAlwaysOnSwitch` class.

The switch uses the unique ID suffix `_oled_always_on`.

### OLED Always On Switch Is Unavailable

The switch requires the `oled_sleep_timeout` setting to be present in the Pironman API response.

Check the configuration endpoint:

```bash
curl http://PIRONMAN_IP:34001/api/v1.0/get-config
```

Verify that the returned system configuration includes `oled_sleep_timeout`.

If the setting is missing, check the installed Pironman software and API compatibility.

### OLED Still Turns Off with Always On Enabled

- Confirm the main OLED switch is enabled.
- Check that the reported sleep timeout is `0`.
- Verify that the Pironman software supports a zero-second timeout.
- Check whether another application or service is modifying the OLED configuration.
- Review the Home Assistant and Pironman service logs.

The Always On feature disables the automatic sleep timer; it does not prevent the display from being turned off manually or during shutdown.

### Previous OLED Timeout Was Not Restored

The integration remembers the previous positive timeout only during the current Home Assistant session.

If Home Assistant or the integration restarts while Always On is active, the original timeout may no longer be known.

In that case, disabling Always On restores the default fallback of **10 seconds**.

You can set your preferred timeout again using the **OLED Sleep Timeout** entity.

### Configuration Changes Do Not Apply

Save the integration options and allow Home Assistant to reload the integration.

If the problem persists, restart Home Assistant and check the logs.

## Roadmap

Potential future improvements include:

- Automatic NVMe and USB storage discovery
- Additional hardware monitoring entities
- Expanded diagnostics and troubleshooting
- Persistent storage of the previous OLED timeout
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
