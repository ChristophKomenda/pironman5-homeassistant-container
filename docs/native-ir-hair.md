# Native IR receiver / HAIR (experimental) — v1.5.0

This feature is **receive-only** and **opt-in**. It has been tested on the
Pironman 5 Max with an RC-5 remote and HAIR, but not on other case models.

## Home Assistant (HACS)

Update **Pironman 5** to v1.5.0 in HACS, then restart Home Assistant.
In the existing Pironman 5 config entry's **Options / Configure**, enable
"Enable experimental native infrared receiver" and set its bridge ID.
The ID must be unique per host and match the value passed to the host service.
Do not enable this feature on other devices that do not have a tested receiver.

## Host bridge (required; HACS cannot install systemd host software)

On the Raspberry Pi carrying the IR receiver, download the release source
archive or clone the repository. The receiver must appear as `/dev/lircN`.
Store a Home Assistant long-lived token in `/root/.config/pironman-ir/ha-token`
with root-only permissions (0600). Never place tokens in a repository.

Preview the unit:

```bash
sudo python3 ir_bridge/host/install_service.py --device-id raspberrypi
```

Install and enable it on a new host:

```bash
sudo python3 ir_bridge/host/install_service.py --device-id raspberrypi --enable
```

The default HA URL is `http://127.0.0.1:8123`; override with `--ha-url`
when HA is on another machine. Existing v0.6 host installs can continue to
run unchanged (do not run the installer a second time without reviewing).

## Verification

```bash
systemctl is-enabled pironman-ir-raw
systemctl is-active pironman-ir-raw
sudo journalctl -u pironman-ir-raw -n 30 --no-pager
```

Open HAIR → Sniffer and choose the new receiver from the **Pironman 5**
integration. Remove the old `pironman_ir_experimental` integration only after
verifying the new receiver and its HAIR assignments.

## Limitations / security

- Raw pulse/space sequences preserve the RC-5 toggle information; the host
  bridge does not itself decode the toggle bit or guarantee press/release events.
- Linux input event numbers and LIRC device numbers can change after reboot;
  the host bridge includes device rediscovery and reconnection.
- Events are sent over the HA REST API; an outage can lose IR frames.
- HAIR may show an inferred 38 kHz carrier; GPIO receiver does not measure it.
- Access to the Home Assistant API token is sensitive. Use a trusted network.
- Testing is limited to Pironman 5 Max; no claims for other models.
