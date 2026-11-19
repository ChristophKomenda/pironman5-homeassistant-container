#!/usr/bin/env python3
"""Experimental Pironman raw IR -> HA native receiver bridge (v0.5).

Reads MODE2 pulse/space records from /dev/lirc0 and sends complete frames to
Home Assistant's event bus. Install the companion pironman_ir_experimental
custom integration to expose InfraredReceiverEntity to HAIR.

This is receiver-only, experimental, and intentionally separate from v0.4.
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
import glob
import json
import logging
import os
from pathlib import Path
import queue
import select
import signal
import socket
import stat
import struct
import threading
import time
from urllib import error, request
from urllib.parse import urlsplit

LOG = logging.getLogger('pironman_ir_raw')
STOP = threading.Event()
LIRC_WORD = struct.Struct('=I')
TYPE_MASK = 0xff000000
VALUE_MASK = 0x00ffffff
SPACE, PULSE, FREQUENCY, TIMEOUT, OVERFLOW = 0, 0x01000000, 0x02000000, 0x03000000, 0x04000000
EVENT_NAME = 'pironman5_ir_raw_received'


def find_receivers() -> list[str]:
    """Map gpio_ir_recv kernel rc devices to their actual LIRC character nodes."""
    devices = []
    for name in glob.glob('/sys/class/rc/rc*'):
        rc = Path(name)
        try:
            driver_link = (rc / 'device').resolve()
            if 'ir-receiver@' not in str(driver_link):
                continue
            for item in rc.glob('lirc*'):
                path = Path('/dev') / item.name
                if path.is_char_device():
                    devices.append(str(path))
        except OSError:
            continue
    return sorted(set(devices))


def validate_url(url: str) -> str:
    p = urlsplit(url)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password or p.query or p.fragment or p.path not in ('', '/'):
        raise ValueError('--ha-url must be an HTTP(S) origin (no path/credentials)')
    return url.rstrip('/')


def token_from_file(path: str) -> str:
    p = Path(path)
    s = p.stat()
    if not stat.S_ISREG(s.st_mode):
        raise ValueError('Token file is not a regular file')
    if s.st_mode & 0o077:
        LOG.warning('Token permissions are broad; use chmod 600 %s', path)
    token = p.read_text(encoding='utf-8').strip()
    if not token:
        raise ValueError('Token file is empty')
    return token


class Frames:
    """Turn LIRC MODE2 words into signed pulse/space timing frames."""

    def __init__(self, gap_us: int = 12000, min_edges: int = 8, max_edges: int = 512):
        self.gap_us = gap_us
        self.min_edges = min_edges
        self.max_edges = max_edges
        self.timings: list[int] = []
        self.carrier: int | None = None

    def flush(self) -> dict | None:
        timings = self.timings
        self.timings = []
        if len(timings) < self.min_edges or len(timings) > self.max_edges:
            return None
        if not any(t > 0 for t in timings) or not any(t < 0 for t in timings):
            return None
        return {'timings': timings, 'modulation': self.carrier}

    def ingest(self, word: int) -> list[dict]:
        kind, value = word & TYPE_MASK, word & VALUE_MASK
        emitted = []
        if kind == FREQUENCY:
            if 20000 <= value <= 100000:
                self.carrier = value
            return emitted
        if kind == OVERFLOW:
            self.timings.clear()
            return emitted
        if kind == TIMEOUT:
            frame = self.flush()
            if frame:
                emitted.append(frame)
            return emitted
        if kind not in (PULSE, SPACE) or value <= 0:
            return emitted
        if kind == SPACE and value >= self.gap_us:
            frame = self.flush()
            if frame:
                emitted.append(frame)
            return emitted
        new = value if kind == PULSE else -value
        if not self.timings and new < 0:
            return emitted
        if self.timings and (self.timings[-1] > 0) == (new > 0):
            self.timings[-1] += new
        else:
            self.timings.append(new)
        if len(self.timings) > self.max_edges:
            self.timings.clear()
        return emitted


def sender(url: str, token: str, outbox: queue.Queue) -> None:
    endpoint = url + '/api/events/' + EVENT_NAME
    while not STOP.is_set() or not outbox.empty():
        try:
            event = outbox.get(timeout=0.25)
        except queue.Empty:
            continue
        try:
            req = request.Request(endpoint, data=json.dumps(event).encode(), method='POST',
                                  headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'})
            with request.urlopen(req, timeout=4) as response:
                response.read()
            LOG.info('Delivered raw frame (%s timings)', len(event['timings']))
        except error.HTTPError as e:
            LOG.error('HA returned HTTP %s', e.code)
        except (error.URLError, TimeoutError, OSError) as e:
            LOG.warning('Unable to send raw signal: %s', e)
        finally:
            outbox.task_done()


def listen(device: str, device_id: str, frames: Frames, outbox: queue.Queue | None, print_json: bool) -> None:
    fd = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
    pending = b''
    LOG.info('Receiving raw IR on %s', device)
    try:
        while not STOP.is_set():
            ready, _, _ = select.select([fd], [], [], 0.5)
            if not ready:
                continue
            try:
                data = os.read(fd, 4096)
            except BlockingIOError:
                continue
            if not data:
                raise OSError('LIRC device disconnected')
            pending += data
            while len(pending) >= 4:
                word = LIRC_WORD.unpack(pending[:4])[0]
                pending = pending[4:]
                for frame in frames.ingest(word):
                    event = {'device_id': device_id, 'timings': frame['timings'],
                             'modulation': frame['modulation'],
                             'timestamp': datetime.now(timezone.utc).isoformat(timespec='milliseconds')}
                    if print_json:
                        print(json.dumps(event, separators=(',', ':')), flush=True)
                    else:
                        LOG.info('Captured raw frame (%s timings)', len(event['timings']))
                    if outbox is not None:
                        try:
                            outbox.put_nowait(event)
                        except queue.Full:
                            LOG.warning('Dropping raw frame (send queue full)')
    finally:
        os.close(fd)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--list-devices', action='store_true')
    ap.add_argument('--device', help='Override /dev/lircN automatic detection')
    ap.add_argument('--device-id', default=socket.gethostname(), help='Must match the ID configured in Home Assistant')
    ap.add_argument('--ha-url', help='HA origin, e.g. http://127.0.0.1:8123')
    ap.add_argument('--token-file', help='Path to the Home Assistant long-lived token file')
    ap.add_argument('--gap-us', type=int, default=12000)
    ap.add_argument('--reconnect-seconds', type=float, default=3)
    ap.add_argument('--quiet', action='store_true', help='Hide per-frame JSON (log short summaries instead)')
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    if args.list_devices:
        print('\n'.join(find_receivers()) or 'No gpio_ir_recv LIRC devices discovered')
        return 0
    if args.gap_us < 3000 or args.reconnect_seconds <= 0 or not args.device_id.strip():
        ap.error('Invalid gap, reconnect delay or device ID')
    if bool(args.ha_url) != bool(args.token_file):
        ap.error('Provide --ha-url and --token-file together')
    q = None
    if args.ha_url:
        try:
            url = validate_url(args.ha_url)
            token = token_from_file(args.token_file)
        except (OSError, ValueError) as e:
            ap.error(str(e))
        q = queue.Queue(maxsize=100)
        threading.Thread(target=sender, args=(url, token, q), daemon=True).start()
        LOG.info('Forwarding raw frames to Home Assistant: %s', EVENT_NAME)
    else:
        LOG.info('Print-only mode')
    def stop(_signum, _frame):
        STOP.set()
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    while not STOP.is_set():
        devices = [args.device] if args.device else find_receivers()
        if len(devices) != 1:
            LOG.warning('Expected one receiver, found %s; retrying', len(devices))
        else:
            try:
                listen(devices[0], args.device_id, Frames(gap_us=args.gap_us), q, not args.quiet)
            except (OSError, ValueError) as e:
                if not STOP.is_set():
                    LOG.warning('Receiver disconnected or busy: %s', e)
        STOP.wait(args.reconnect_seconds)
    LOG.info('Stopped')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
