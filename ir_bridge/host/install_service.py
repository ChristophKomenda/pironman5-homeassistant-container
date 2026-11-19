#!/usr/bin/env python3
"""Install an independent raw-IR systemd host listener with safe token handling."""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

SRC = Path(__file__).with_name('pironman_ir_raw_v06.py')
DEST = Path('/usr/local/libexec/pironman-ir-raw.py')
UNIT = Path('/etc/systemd/system/pironman-ir-raw.service')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--device-id', required=True, help='Unique per machine, same as HA option')
    ap.add_argument('--ha-url', default='http://127.0.0.1:8123')
    ap.add_argument('--token-file', default='/root/.config/pironman-ir/ha-token')
    ap.add_argument('--enable', action='store_true', help='Actually install, enable and start')
    a = ap.parse_args()
    if not a.device_id.strip() or len(a.device_id) > 64 or any(c.isspace() for c in a.device_id) or any(c in a.device_id for c in "'\"\\"):
        ap.error('device-id must be 1-64 characters, no whitespace or quotes')
    if not a.ha_url.startswith(('http://', 'https://')) or any(x in a.ha_url for x in ('\n', '\r', ' ', '"', "'")):
        ap.error('Invalid HA URL')
    token = Path(a.token_file)
    if not token.is_file():
        ap.error(f'Token file not found: {token}')
    if not token.is_absolute() or any(x in str(token) for x in ('\n', '\r', '"', "'", ' ')):
        ap.error('Use an absolute token file path without spaces or quotes')
    unit = f'''[Unit]
Description=Pironman 5 raw IR receiver (native HAIR)
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 {DEST} --device-id {a.device_id} --ha-url {a.ha_url} --token-file {token} --quiet
Restart=always
RestartSec=5
TimeoutStopSec=10
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=true

[Install]
WantedBy=multi-user.target
'''
    print(unit)
    if not a.enable:
        print('Preview only. Add --enable to install and start.')
        return
    if UNIT.exists():
        ap.error(f'{UNIT} already exists; will not overwrite it automatically')
    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, DEST)
    DEST.chmod(0o755)
    UNIT.write_text(unit)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    subprocess.run(['systemctl','enable','--now',UNIT.name],check=True)
    print('Installed:',UNIT)

if __name__=='__main__':
    main()
