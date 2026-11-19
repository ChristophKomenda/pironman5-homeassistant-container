# v1.5.0 — Native IR Receiver & HAIR Support

Regular GitHub release. **IR support remains experimental and opt-in.**

Adds an opt-in Home Assistant native IR receiver to the existing Pironman 5
integration, allowing the built-in Pironman 5 Max infrared receiver to work
with HAIR — without additional ESPHome IR hardware.

### Included
- Optional `infrared` platform and receiver entities within existing Pironman config entries.
- Per-entry bridge IDs for multi-host setups.
- Host-side raw-LIRC bridge with reconnect handling and systemd autostart installer.
- Raw RC-5 frame forwarding (including its encoded toggle information).
- Setup guide and automated offline unit tests.

### Important
- **Experimental**: tested on Pironman 5 Max and HAIR, not all Pironman variants.
- Receive-only. No IR transmitter.
- A separate Python/systemd host service is still required; HACS cannot install it.
- Existing v0.6 bridge users do not need to reinstall the running service.
- The bridge does not decode the RC-5 toggle bit into separate press/release events.
- API outages can cause missed IR frames.

Installation: [Native IR / HAIR guide](docs/native-ir-hair.md).

Documentation: [README](README.md) · [Host bridge](ir_bridge/README.md).
