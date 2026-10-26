# Hardware compatibility and testing

This document tracks **verified hardware configurations** and provides a reproducible test plan for the community. It is not a promise of compatibility with untested Pironman variants.

## Compatibility matrix

| Hardware | Integration support | Verification status | Notes |
| --- | --- | --- | --- |
| SunFounder Pironman 5 Max | Supported | Maintainer-tested | Raspberry Pi 5, Home Assistant Container; features depend on the installed Pironman software/API. |
| SunFounder Pironman 5 | Targeted | Not maintainer-tested | Uses the Pironman software's local REST API. Please report the exact hardware/software combination if you test it. |
| SunFounder Pironman Mini | Not confirmed | Not tested | API availability and compatibility must be checked before support can be claimed. |
| SunFounder Pironman Pro Max | Not confirmed | Not tested | API availability and compatibility must be checked before support can be claimed. |
| Other Pironman variants | Not confirmed | Not tested | No compatibility claims without evidence. |

**Important:** “Supported” describes the intended integration target. “Maintainer-tested” means the maintainer has used that hardware configuration directly. The presence of a compatible REST endpoint alone does not guarantee feature parity.

## Known deployment scenarios

- Home Assistant Container (Docker) on the Pironman Raspberry Pi — maintainer-tested on Pironman 5 Max.
- Home Assistant on another device on the same trusted LAN — supported by the network-based API design; individual deployments may vary.
- Other Home Assistant installations that can reach the Pironman REST API — expected to work, but not all combinations have been individually verified.

## Prerequisites

- Pironman software installed and running on the target Raspberry Pi.
- Local REST API reachable from Home Assistant (default TCP port `34001`).
- Home Assistant 2024.1.0 or newer, as specified by `hacs.json`.
- A trusted local network; **do not expose the Pironman API to the internet**.

The Home Assistant integration does not directly access GPIO or I²C; the Pironman software handles hardware communication.

## Test record template

Copy this section into a GitHub issue or pull request when reporting compatibility results. Remove private information before posting.

```text
Pironman model:
Raspberry Pi model:
Operating system and version:
Pironman software version:
Home Assistant version:
Home Assistant installation type (Container / OS / other):
Integration version:
API endpoint reachable from Home Assistant? (yes/no):
API port (default 34001):

Installation and configuration: PASS / FAIL / NOT TESTED
CPU / GPU / memory sensors: PASS / FAIL / NOT TESTED
NVMe sensors (state number of installed drives): PASS / FAIL / NOT TESTED
Network sensors: PASS / FAIL / NOT TESTED
Fan speed and profiles: PASS / FAIL / NOT TESTED
RGB power / color / effects: PASS / FAIL / NOT TESTED
OLED controls / sleep timeout: PASS / FAIL / NOT TESTED
Reload after changing host / port / polling: PASS / FAIL / NOT TESTED
Restart persistence and entity availability: PASS / FAIL / NOT TESTED

Notes, missing API fields, and redacted logs:
```

## Second-device validation plan

A second physical Pironman setup would allow independent validation without disturbing the maintainer's primary system:

1. **Baseline:** Record hardware, OS, Pironman software, Home Assistant and integration versions.
2. **Fresh install:** Install through HACS and complete the configuration flow.
3. **Connectivity:** Confirm that Home Assistant can reach the local REST API from its own runtime/network namespace.
4. **Read-only entities:** Compare CPU, GPU, memory, NVMe, network and fan readings against the upstream Pironman interface where available.
5. **Controls:** Test fan profiles, RGB effects and OLED settings, checking that the upstream API reflects each change.
6. **Edge cases:** Check missing hardware, missing API fields, unavailable sensors, API downtime and reconnection.
7. **Configuration:** Change host, port and polling interval; verify clean reload and recovery.
8. **Stability:** Observe repeated polling and normal Home Assistant restarts; record errors and unexpected behavior.
9. **Evidence:** Publish a redacted test report and screenshots; update the compatibility matrix only after verification.

## Contributing test results

Open an issue at https://github.com/ChristophKomenda/pironman5-homeassistant-container/issues and include the test record above. Do not publish tokens, private IP addresses, or unredacted logs.

This is a community-maintained integration and is not official SunFounder software.
