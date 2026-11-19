# Pironman 5 v1.5.0 — Host IR bridge for HAIR

The optional **receive-only** IR receiver is integrated in the existing
**Pironman 5** HACS integration (v1.5.0). The Python host listener in this
folder is the required companion for reading `/dev/lircN` on a supported
Raspberry Pi. **HACS cannot install or manage host-side systemd services.**

The IR feature remains **experimental**, even though v1.5.0 is a regular
GitHub release. Verified hardware: **Pironman 5 Max**, using an RC-5 remote
with HAIR. Other Pironman models have not been validated.

## Requirements

- Linux Raspberry Pi host with `gpio_ir_recv` and a working `/dev/lircN`
  (try `ls -l /dev/lirc*` and `sudo mode2 -d /dev/lirc0`).
- Home Assistant with native infrared support and the **Pironman 5 v1.5.0**
  HACS integration; HAIR is optional but recommended for testing and learning.
- Python 3, systemd and a Home Assistant long-lived access token.
- IP connectivity from the Pi to the Home Assistant API; use a trusted LAN.

## Installation

Clone the repository or download the v1.5.0 release source archive on the
Raspberry Pi hosting the receiver, then change to the repository root.

Create and protect the API token file **on the Pi**:

```bash
sudo install -d -m 700 /root/.config/pironman-ir
sudo nano /root/.config/pironman-ir/ha-token
sudo chmod 600 /root/.config/pironman-ir/ha-token
```

Paste only the token in the file. Never include tokens in issues or commits.

Preview the systemd service before installing (run from repository root):

```bash
sudo python3 ir_bridge/host/install_service.py --device-id raspberrypi
```

Install and enable (adapt `--ha-url` for a separate HA host):

```bash
sudo python3 ir_bridge/host/install_service.py --device-id raspberrypi --enable
```

The default API URL is `http://127.0.0.1:8123`; this only works when Home
Assistant is reachable from the **host** at that address. Read the installer's
`--help` before selecting another URL, token path or device ID.

Under **Settings → Devices & services → Pironman 5 → Configure**, enable
**Enable experimental native infrared receiver** on the relevant entry and
set **IR bridge device ID** to `raspberrypi` (or the unique ID chosen above).
Do not enable the receiver on other Pironman entries without their own host listener.

## Verify

```bash
systemctl is-enabled pironman-ir-raw
systemctl is-active pironman-ir-raw
sudo journalctl -u pironman-ir-raw -n 30 --no-pager
```

Select the new **Pironman 5** IR receiver in **HAIR → Sniffer** and press a
button on an infrared remote. If an older standalone experimental receiver
exists, remove it **only after** switching HAIR to the new one.

## Behavior and limitations

- The bridge forwards raw pulse/space data; RC-5 toggle information is
  retained in the waveform but is **not decoded by the bridge**.
- Long-held buttons produce repeated frames; HAIR decides how to group them.
- The host listener rediscovers `/dev/lircN` after device renumbering and
  systemd restarts it after process failures.
- Offline API periods can lose IR events; this is not a guaranteed-delivery bus.
- IR receive only; a separate transmitter is needed for IR output.
- Do not expose the HA REST API or the Pironman REST API to the internet.

## Uninstall host listener

```bash
sudo systemctl disable --now pironman-ir-raw
```

This disables the optional host listener, not the main Pironman integration.
See [full guide](../docs/native-ir-hair.md) for further information.

## Development

The host service is `host/pironman_ir_raw_v06.py`, installed with
`host/install_service.py`. Offline unit tests:

```bash
python3 -m unittest discover -s ir_bridge/tests -v
```
