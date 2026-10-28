# Hardware compatibility and testing

> **Current release:** [v1.2.0 — Multi-Model Support & Automatic Hardware Detection](https://github.com/ChristophKomenda/pironman5-homeassistant-container/releases/tag/v1.2.0)
>
> Published October 28, 2026. This document distinguishes implemented model support from functionality verified on physical hardware.


This document tracks **verified hardware configurations** and provides a reproducible test plan for the community. It is not a promise of compatibility with untested Pironman variants.

## Compatibility matrix

| Hardware | Implementation | Verification status | Notes |
| --- | --- | --- | --- |
| SunFounder Pironman 5 Max | Model detection and capability-aware entities implemented | **Maintainer-tested** | Home Assistant Container 2026.10.1; Pironman API 1.3.20; successful startup and capability checks. Individual controls have not all been revalidated as part of v1.2.0. |
| SunFounder Pironman 5 | Model detection and capability-aware entities implemented | Not tested for v1.2.0 | Real-hardware verification needed. |
| SunFounder Pironman 5 Mini | Model detection and capability-aware entities implemented | Not tested | API and available controls must be verified on real hardware. |
| SunFounder Pironman 5 Pro Max | Model detection and capability-aware entities implemented | Not tested | API and available controls must be verified on real hardware. |
| Other Pironman variants | Not confirmed | Not tested | No compatibility claims without evidence. |

**Important:** An implemented model selector is not the same as verified hardware compatibility. Capability-aware setup uses the `peripherals` list from `/get-device-info` when available. Missing capability metadata triggers legacy behavior, not a guarantee that every entity is supported. Manual selection does not add missing hardware capabilities.

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
Automatic model detection (model key / source):
Manual override tested? (yes/no):
Reported peripherals (redact identifying details):
Raspberry Pi model:
Operating system and version:
Pironman software version:
Home Assistant version:
Home Assistant installation type (Container / OS / other):
Integration version:
API endpoint reachable from Home Assistant? (yes/no):
API port (default 34001):

Installation and configuration: PASS / FAIL / NOT TESTED
Automatic detection and model sensor: PASS / FAIL / NOT TESTED
Manual model override and reload: PASS / FAIL / NOT TESTED
Capability-aware entity visibility: PASS / FAIL / NOT TESTED
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

## Verification scope for v1.2.0

The following checks have been completed on the maintainer's Pironman 5 Max setup:

- Successful Home Assistant integration startup.
- Automatic detection of the Pironman 5 Max model.
- Retrieval and interpretation of API-reported hardware capabilities.
- Successful Home Assistant operation without reported startup errors.

**Verification limitations:**

- Individual OLED, RGB and fan control operations have not all been independently revalidated for v1.2.0.
- Pironman 5, Pironman 5 Mini and Pironman 5 Pro Max still require physical hardware testing.
- Manual model selection does not guarantee the availability of model-specific hardware controls.

This section should be updated as additional test results become available.

## Contributing test results

Open an issue at https://github.com/ChristophKomenda/pironman5-homeassistant-container/issues and include the test record above. Do not publish tokens, private IP addresses, or unredacted logs.

This is a community-maintained integration and is not official SunFounder software.
