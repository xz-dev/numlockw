#!/usr/bin/env python3
"""
evdev-holder: Keep evdev input device file descriptors permanently open.

Workaround for LED pulsing on certain hardware (e.g. Tuxedo Stellaris 15 Gen3).

Root cause:
  When all fds to /dev/input/eventX are closed, the kernel's evdev->open count
  drops to 0. The next open() triggers:
    evdev_open_device() -> input_open_device() -> dev->open()
  which calls the hardware driver callback (e.g. hidinput_open -> hid_hw_open).
  On affected firmware (e.g. Tuxedo Stellaris EC), this driver reinitialization
  causes a visible LED pulse as a side effect.

Fix:
  By keeping at least one fd open per device, evdev->open stays >= 1. Subsequent
  opens see a truthy evdev->open++ and skip input_open_device() entirely, so the
  LED re-assertion path is never reached.

See:
  https://www.reddit.com/r/tuxedocomputers/comments/1rtj3c9/
  https://github.com/gvalkov/python-evdev/pull/251

Usage:
  sudo python3 evdev_holder.py            # foreground
  sudo python3 evdev_holder.py --quiet    # suppress info messages

Pure stdlib Python. No external dependencies.
"""

import argparse
import glob
import logging
import os
import signal
import sys
import time

DEVPATH = "/dev/input/event*"
DEFAULT_INTERVAL = 5  # seconds

log = logging.getLogger("evdev-holder")


def discover_devices():
    """Return sorted list of all /dev/input/event* paths."""
    return sorted(glob.glob(DEVPATH))


def open_device(path):
    """Open a device read-only + nonblock. Returns fd or None on failure."""
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        return fd
    except OSError as e:
        log.warning("cannot open %s: %s", path, e)
        return None


def fd_is_alive(fd):
    """Check if a held fd is still valid (device not unplugged)."""
    try:
        os.fstat(fd)
        return True
    except OSError:
        return False


def close_fd(fd):
    """Close a file descriptor, ignoring errors."""
    try:
        os.close(fd)
    except OSError:
        pass


class EvdevHolder:
    def __init__(self, interval=DEFAULT_INTERVAL):
        # path -> fd
        self.held = {}
        self.interval = interval

    def scan(self):
        """Open any new devices not already held. Drop dead ones."""
        # prune dead fds
        dead = [p for p, fd in self.held.items() if not fd_is_alive(fd)]
        for path in dead:
            log.info("device removed: %s", path)
            close_fd(self.held.pop(path))

        # open new devices
        for path in discover_devices():
            if path not in self.held:
                fd = open_device(path)
                if fd is not None:
                    self.held[path] = fd
                    log.info("holding: %s (fd=%d)", path, fd)

    def close_all(self):
        """Close all held file descriptors."""
        for path, fd in self.held.items():
            log.debug("releasing: %s (fd=%d)", path, fd)
            close_fd(fd)
        count = len(self.held)
        self.held.clear()
        return count

    def run(self):
        """Main loop: scan, sleep, repeat."""
        self.scan()
        log.info("initial scan: holding %d device(s)", len(self.held))

        while True:
            time.sleep(self.interval)
            self.scan()


def main():
    parser = argparse.ArgumentParser(
        description="Hold evdev input devices open to prevent LED pulsing on affected hardware."
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Only show warnings and errors.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help=f"Device rescan interval in seconds (default: {DEFAULT_INTERVAL}).",
    )
    args = parser.parse_args()

    # logging setup
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("[evdev-holder] %(message)s"))
    log.addHandler(handler)
    log.setLevel(logging.WARNING if args.quiet else logging.INFO)

    holder = EvdevHolder(interval=args.interval)

    # graceful shutdown
    def shutdown(signum, _frame):
        signame = signal.Signals(signum).name
        log.info("received %s, releasing all devices...", signame)
        count = holder.close_all()
        log.info("released %d device(s), exiting", count)
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    log.info("starting (rescan interval: %.1fs)", args.interval)
    holder.run()


if __name__ == "__main__":
    main()
