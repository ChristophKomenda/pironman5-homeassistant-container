# Security Policy

## Supported versions

Security fixes are targeted at the latest stable release. Older releases may not receive security updates.

## Reporting a vulnerability

Please **do not open a public issue** for a suspected security vulnerability.

If GitHub Private Vulnerability Reporting is enabled, use **Security → Report a vulnerability** in this repository. Otherwise contact the maintainer privately through an agreed secure channel. Do not send exploits or secrets through public discussions.

Include the affected versions, a concise description, reproduction steps, and potential impact. Please allow reasonable time for investigation and coordinated disclosure.

## Network security

This integration uses the Pironman local REST API, normally on TCP port `34001`.

- Keep the API accessible only to trusted devices on your LAN.
- Never expose port `34001` directly to the public internet.
- Use firewall rules and network segmentation where appropriate.
- Keep Home Assistant, the integration, and upstream Pironman software updated.
- Remove tokens, credentials, personal data, and public IPs from shared logs.

## Scope

This repository maintains the Home Assistant integration, not the upstream SunFounder Pironman software. Please also notify upstream maintainers if the vulnerability affects their software.
