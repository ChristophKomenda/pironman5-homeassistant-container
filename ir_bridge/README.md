# Pironman 5 — Native IR / HAIR integration (v0.6 experimental)

A **local integration patch**, not an official release. Targets the currently examined `pironman5` v1.4.0 HACS code. The host-side LIRC bridge and the existing Pironman REST API perform separate jobs.

## Features / boundaries

- New **optional** `infrared` platform in the EXISTING `pironman5` config entry. Uses native `InfraredReceiverEntity` and publishes raw IR frames to HAIR.
- Receiver uses existing Pironman device registry identity; no second custom integration is needed in the eventual HACS release.
- Supports **multiple hosts**: every existing Pironman config entry chooses its own bridge ID. Use a unique bridge ID per Pi and a separate listener/token on each host.
- Raw RC5 telegrams are transmitted **unchanged**, including toggle information encoded in the waveform. Held-button telegrams are **not suppressed**; HAIR's decoder can distinguish them. This implementation does not independently parse or classify the RC5 toggle bit.
- The bridge reconnects if `/dev/lircN` disappears or Linux renumbers the device, and a systemd unit restarts it after crashes/reboots. It does **not** guarantee zero loss of events during Wi-Fi/HA outages; the queue is bounded and failed POSTs are not retried.
- Only **IR receive**. Requires Home Assistant with native infrared platform (confirmed on the user's HA). The host must expose Linux `/dev/lircN` via gpio-ir-recv. No new pip packages.
- **Not yet field-tested as combined v0.6**. Previous separate v0.5 bridge and `pironman_ir_experimental` entity were tested successfully with HAIR.

## Before install

Make a Home Assistant backup or snapshot first. Keep the existing v0.4 decoded-event bridge running if you need its automation events. Use a separate systemd service for raw reception.

When ready to migrate, **remove the old Pironman IR Receiver (Experimental) config entry via Home Assistant UI**. Doing so can remove its old IR entity association in HAIR. Plan to reassign the new receiver in HAIR if necessary. Do not delete the existing `pironman5` HACS integration.

## Installation on the Raspberry Pi

1. Download `pironman-ir-v06.zip` and copy it to `/home/admin/` using SCP.
2. Unpack into `/home/admin/pironman-ir-v06`:
   ```bash
   cd /home/admin && unzip -o pironman-ir-v06.zip
   ```
3. Validate patch without changing anything:
   ```bash
   sudo python3 /home/admin/pironman-ir-v06/install_v06.py
   ```
4. Remove the **old experimental** config entry under Settings > Devices & services (not the existing `pironman5` integration). Then apply:
   ```bash
   sudo python3 /home/admin/pironman-ir-v06/install_v06.py --apply
   ```
   The installer creates a full directory backup `.../custom_components/pironman5_ir_backup_<UTC stamp>` and changes only `__init__.py`, `config_flow.py`, `strings.json` and adds `infrared.py`. It will refuse unknown code layouts.
5. Restart Home Assistant:
   ```bash
   docker restart homeassistant
   ```
6. In existing **Pironman 5 > Configure/Options**, turn on **Enable experimental native infrared receiver** and set IR bridge device ID to `raspberrypi`. Other devices should use distinct IDs, e.g. `pironman-living-room`, `pironman-office`.
7. Configure systemd **after you verify** `/root/.config/pironman-ir/ha-token` exists and its permissions are 0600. Preview the unit:
   ```bash
   sudo python3 /home/admin/pironman-ir-v06/host/install_service.py --device-id raspberrypi
   ```
   Then install and enable:
   ```bash
   sudo python3 /home/admin/pironman-ir-v06/host/install_service.py --device-id raspberrypi --enable
   ```
   Default Home Assistant endpoint `http://127.0.0.1:8123` and token file path match your tested setup.
8. Test:
   ```bash
   systemctl is-enabled pironman-ir-raw
   systemctl is-active pironman-ir-raw
   sudo journalctl -u pironman-ir-raw -n 30 --no-pager
   ```
   Then open HAIR Sniffer and check the receiver under the **existing Pironman 5 device**.

## Rollback

```bash
sudo systemctl disable --now pironman-ir-raw
sudo rm -f /etc/systemd/system/pironman-ir-raw.service
sudo systemctl daemon-reload
```

To revert the HA patch, **restore the backed-up `pironman5` directory** created by the installer (after stopping HA), then restart Home Assistant. `install_v06.py` prints the backup directory. HACS updates can replace manual edits until the changes are merged/released upstream.

## Developer / GitHub PR

The integration feature consists of new `custom_components/pironman5/infrared.py` plus modifications to `__init__.py`, `config_flow.py`, `strings.json`. The host service in `host/` is an optional separately installed companion; HACS alone **cannot install a systemd service on the host**. The code should be reviewed and CI-tested against the current default branch before publishing. Do not advertise Pro Max compatibility without hardware testing.

## Run tests

```bash
python3 -m unittest discover -s tests -v
```
