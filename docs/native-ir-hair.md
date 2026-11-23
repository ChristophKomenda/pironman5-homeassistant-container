# Native IR receiver / HAIR — v1.5.0 (experimental feature)

**v1.5.0 is a regular GitHub release; the optional IR receiver feature is experimental.**
This feature is **receive-only** and **opt-in**. It has been tested on the
Pironman 5 Max with an RC-5 remote and HAIR, but not on other case models.
No additional ESPHome IR hardware is needed for reception, but a separate
IR listener is required: **a community add-on on HAOS** or **a Python/systemd
host-side service on Home Assistant Container**.

## Home Assistant (HACS)

Update **Pironman 5** to v1.5.0 in HACS, then restart Home Assistant.
In the existing Pironman 5 config entry's **Options / Configure**, enable
"Enable experimental native infrared receiver" and set its bridge ID.
The ID must be unique per host and match the value passed to the host service.
Do not enable this feature on other devices that do not have a tested receiver.

## Home Assistant Container: host bridge (required for the Container IR route)

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

## Multiple Pironman devices

Configure IR individually on each existing Pironman config entry. Every host
needs its own Linux receiver and host listener. Use **different device IDs**
(e.g. `raspberrypi-office`, `raspberrypi-living-room`) and match the configured
ID to `--device-id`. A single listener does not magically enable a second Pi.

## Verification

```bash
systemctl is-enabled pironman-ir-raw
systemctl is-active pironman-ir-raw
sudo journalctl -u pironman-ir-raw -n 30 --no-pager
```

Open HAIR → Sniffer and choose the new receiver from the **Pironman 5**
integration. Remove the old `pironman_ir_experimental` integration only after
verifying the new receiver and its HAIR assignments.

## Troubleshooting

If no receiver appears in HAIR, confirm the correct Pironman 5 entry has IR
enabled, the bridge ID matches, and the host listener is active. Verify raw
frames with `sudo mode2 -d /dev/lirc0` **only while the raw bridge is stopped**,
then restart the service. Check the Home Assistant logs for `pironman5` or
`infrared` errors. An HTTP API success does not by itself prove HAIR received
and decoded a frame.

If the systemd host service is active but no frames are received, check which
`/dev/lircN` device belongs to `gpio_ir_recv` and that IR reception works on
that host. If you previously used `pironman_ir_experimental`, ensure HAIR has
been switched to the new receiver before removing the old entry.

## Limitations / security

- Raw pulse/space sequences preserve the RC-5 toggle information; the host
  bridge does not itself decode the toggle bit or guarantee press/release events.
- Linux input event numbers and LIRC device numbers can change after reboot;
  the host bridge includes device rediscovery and reconnection.
- Events are sent over the HA REST API; an outage can lose IR frames.
- HAIR may show an inferred 38 kHz carrier; GPIO receiver does not measure it.
- Access to the Home Assistant API token is sensitive. Use a trusted network.
- Testing is limited to Pironman 5 Max; no claims for other models.

## Home Assistant OS: community add-on without manual integration copy (validated)

The [community Pironman IR Receiver add-on](https://github.com/ChristophKomenda/home-assistant-addon/tree/main/pironman-ir-receiver)
can be configured with `event_mode: pironman5` and a matching `receiver_id` /
**IR bridge device ID**. The add-on then posts `pironman5_ir_raw_received`
events using its Supervisor API token and this existing HACS integration
provides the native IR entity. No standalone `sunfounder_ir` copy is needed.

On HAOS the Pironman REST API must still be reachable for initial configuration;
`/dev/lirc0` and the Pi GPIO overlay must exist before the IR add-on can work.
This cross-repository pairing was **independently tested on a real HAOS setup**
by [@eugenioparise](https://github.com/eugenioparise) on 23 November 2026.
After selecting `event_mode: pironman5`, disabling the older `sunfounder_ir`
integration, and setting identical receiver IDs, the tester needed to
**reload the Pironman 5 integration** before HAIR successfully captured codes.
Only the Pironman 5 integration receiver was active in HAIR. See the
[community discussion](https://github.com/ChristophKomenda/pironman5-homeassistant-container/discussions/16)
and [add-on release v0.2.0](https://github.com/ChristophKomenda/home-assistant-addon/releases/tag/pironman-ir-v0.2.0).

The built-in GPIO receiver remains **receive-only**. One successful HAOS
setup does not prove universal compatibility. Legacy host-side systemd and
standalone add-on installations remain supported.
