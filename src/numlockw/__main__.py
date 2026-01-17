#!/usr/bin/env python3

import logging
import os
import sys
import time
import traceback
from argparse import ArgumentParser
from typing import List, Optional

import evdev
from evdev import UInput
from evdev.ecodes import EV_KEY, EV_SYN, KEY_NUMLOCK, LED_NUML, SYN_REPORT

UINPOUT_DEVICE_NAME = "numlockw-evdev-uinput"

# Debug mode can be enabled via environment variable NUMLOCKW_DEBUG=1 or --debug flag
DEBUG = os.environ.get("NUMLOCKW_DEBUG", "").lower() in ("1", "true", "yes", "on")

device_name = None
pre_hook = None
led_force = False
fake_uinput = True

# Configure logging
_logger = logging.getLogger("numlockw")
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
_logger.addHandler(_handler)
_logger.setLevel(logging.DEBUG if DEBUG else logging.WARNING)


def _debug(msg: str):
    """Log a debug message."""
    _logger.debug(msg)


def _warn(msg: str):
    """Log a warning message."""
    _logger.warning(msg)


def _check_device_has_numlock(device: evdev.InputDevice) -> bool:
    _debug(f"Checking device '{device.name}' ({device.path}) for NumLock capability")
    cap = device.capabilities()
    has_ev_key = EV_KEY in cap
    has_numlock = has_ev_key and KEY_NUMLOCK in cap[EV_KEY]
    _debug(f"  Device '{device.name}': EV_KEY={has_ev_key}, KEY_NUMLOCK={has_numlock}")
    return has_numlock


def _devices(device_name: Optional[str]) -> List[evdev.InputDevice]:
    _debug(f"Enumerating input devices (filter: {device_name!r})")
    all_paths = evdev.list_devices()
    _debug(f"Found {len(all_paths)} total input devices")

    devices = []
    for path in all_paths:
        _debug(f"Opening device: {path}")
        device = evdev.InputDevice(path)
        _debug(f"  Device name: '{device.name}', phys: '{device.phys}'")
        if _check_device_has_numlock(device):
            devices.append(device)
            _debug(f"  -> Added to NumLock-capable devices list")
        else:
            _debug(f"  -> Skipped (no NumLock capability)")

    _debug(f"Found {len(devices)} devices with NumLock capability")

    result = []
    if device_name is None:
        result = devices[:1]
        _debug(f"No device filter specified, using first device only: {[d.name for d in result]}")
    elif device_name == "*":
        result = devices
        _debug(f"Using all {len(devices)} NumLock-capable devices")
    else:
        result = [device for device in devices if device.name == device_name]
        _debug(f"Filtered by name '{device_name}': found {len(result)} matching devices")
    if not result:
        if device_name is None or device_name == "*":
            raise KeyError("No NumLock-capable devices found")
        else:
            available = [d.name for d in devices]
            raise KeyError(
                f"Device '{device_name}' not found. "
                f"Available NumLock-capable devices: {available}"
            )
    return result


def numlock_switch(devices: List[evdev.InputDevice] = None):
    _debug(f"numlock_switch called (fake_uinput={fake_uinput})")
    if fake_uinput:
        _debug(f"Creating fake UInput device: '{UINPOUT_DEVICE_NAME}'")
        devices = [UInput(name=UINPOUT_DEVICE_NAME)]
        _debug(f"Fake UInput device created successfully")
    else:
        _debug(f"Using {len(devices)} real device(s)")

    for ui in devices:
        _debug(f"Processing device: '{ui.name}'")

        if pre_hook is not None:
            import subprocess

            command_str = pre_hook.replace("${{udevice}}", ui.name)
            _debug(f"Executing pre-hook command: {command_str}")
            result = subprocess.run(command_str, shell=True)
            _debug(f"Pre-hook completed with return code: {result.returncode}")

        _debug(f"Sending KEY_NUMLOCK press event to '{ui.name}'")
        ui.write(EV_KEY, KEY_NUMLOCK, 1)
        ui.write(EV_SYN, SYN_REPORT, 0)
        _debug(f"KEY_NUMLOCK press sent, waiting 50ms for GNOME debounce")

        time.sleep(0.05)  # 50ms, avoid GNOME key debounce

        _debug(f"Sending KEY_NUMLOCK release event to '{ui.name}'")
        ui.write(EV_KEY, KEY_NUMLOCK, 0)
        ui.write(EV_SYN, SYN_REPORT, 0)
        _debug(f"KEY_NUMLOCK release sent")

        _debug(f"Closing device '{ui.name}'")
        ui.close()
        _debug(f"Device '{ui.name}' closed successfully")


def numlock_led_switch(devices: List[evdev.InputDevice], status: bool):
    _debug(f"numlock_led_switch called: setting LED to {'ON' if status else 'OFF'} on {len(devices)} device(s)")
    for device in devices:
        _debug(f"Setting LED_NUML to {1 if status else 0} on device '{device.name}'")
        try:
            device.set_led(LED_NUML, 1 if status else 0)
            _debug(f"LED_NUML set successfully on '{device.name}'")
        except Exception:
            _warn(f"Error setting LED status for device {device.name}")
            _warn(f"Error: {traceback.format_exc()}")


# https://stackoverflow.com/questions/13129804/python-how-to-get-current-keylock-status
def numlock_get_status(device: evdev.InputDevice) -> Optional[bool]:
    _debug(f"Getting NumLock LED status from device '{device.name}'")
    try:
        leds = device.leds()
        status = LED_NUML in leds
        _debug(f"Device '{device.name}' LED status: {'ON' if status else 'OFF'} (active LEDs: {list(leds)})")
        return status
    except Exception:
        _warn(f"Error getting LED status for device {device.name}")
        _warn(f"Error: {traceback.format_exc()}")
        return None


def numlock_get_status_devices(devices: List[evdev.InputDevice]) -> bool:
    _debug(f"Checking NumLock status across {len(devices)} device(s)")
    for device in devices:
        status = numlock_get_status(device)
        if status:
            _debug(f"Found NumLock ON on device '{device.name}', returning True")
            return True
    _debug(f"NumLock is OFF on all devices")
    return False


def toggle(target_status: Optional[bool] = None):
    _debug(f"toggle called with target_status={target_status}")
    _debug(f"Getting devices (device_name={device_name!r})")
    devices = _devices(device_name)
    _debug(f"Got {len(devices)} device(s)")

    status = numlock_get_status_devices(devices)
    _debug(f"Current NumLock status: {'ON' if status else 'OFF'}")

    if target_status is not None and target_status == status:
        _debug(f"Target status {target_status} matches current status, no action needed")
        return

    _debug(f"Status mismatch or no target specified, switching NumLock")
    numlock_switch(devices)

    if led_force:
        _debug(f"force-led enabled, manually setting LED to {'ON' if not status else 'OFF'}")
        numlock_led_switch(devices, not status)
    else:
        _debug(f"force-led disabled, LED will be set by system")

    _debug(f"toggle completed")


def on():
    _debug("on() called - turning NumLock ON")
    toggle(True)


def off():
    _debug("off() called - turning NumLock OFF")
    toggle(False)


def status():
    _debug("status() called - checking NumLock status")
    filter_name = "*" if device_name is None else device_name
    _debug(f"Using device filter: {filter_name!r}")
    devices = _devices(filter_name)
    current_status = numlock_get_status_devices(devices)
    _debug(f"Final status: {'ON' if current_status else 'OFF'}")
    print("NumLock is", "on" if current_status else "off")


def list_devices():
    _debug("list_devices() called")
    _debug(f"Creating temporary UInput device for enumeration")
    with UInput(name=UINPOUT_DEVICE_NAME):
        _debug(f"UInput device created")
        filter_name = "*" if device_name is None else device_name
        _debug(f"Using device filter: {filter_name!r}")
        devices = _devices(filter_name)
        _debug(f"Listing {len(devices)} device(s)")
        print("Path | Device Name | Physical Topology | LED Status")
        for device in devices:
            _debug(f"Getting LED status for device '{device.name}'")
            led_status = numlock_get_status(device)
            print(
                device.path,
                device.name,
                device.phys,
                "N/A" if led_status is None else "ON" if led_status else "OFF",
                sep=" | ",
            )
    _debug("list_devices() completed")


def main():
    parser = ArgumentParser(
        description="numlockw is a program to control the NumLock key, designed for use with Wayland and tty environments."
    )
    parser.add_argument(
        "--device-name",
        type=str,
        default=None,
        help='The name of the input device or "*" for each one. If not provided, will fake keyboard to enable NumLock, and enable LDE_NUML on all devices that support it.',
    )
    parser.add_argument(
        "--no-fake-uinput",
        action="store_true",
        help="Do not fake uinput device, use real devices",
    )
    parser.add_argument(
        "--pre-hook",
        type=str,
        default=None,
        help="A command to run when NumLock is toggled. The command will be run with the status of uinput device name ${{udevice}}.",
    )
    parser.add_argument(
        "--force-led",
        action="store_true",
        help="Force setting LED_NUML on all devices that support it, not dependent system to set it.",
    )
    subparsers = parser.add_subparsers(
        title="actions",
        description="valid actions",
        help="action to perform on NumLock",
        dest="action",
    )
    subparsers.required = True
    # Add parsers for each command
    parser_on = subparsers.add_parser("on", help="Turn NumLock on")
    parser_on.set_defaults(func=on)
    parser_off = subparsers.add_parser("off", help="Turn NumLock off")
    parser_off.set_defaults(func=off)
    parser_toggle = subparsers.add_parser("toggle", help="Toggle NumLock")
    parser_toggle.set_defaults(func=toggle)
    parser_status = subparsers.add_parser("status", help="Display NumLock status")
    parser_status.set_defaults(func=status)
    parser_list_devices = subparsers.add_parser(
        "list-devices", help="List devices that support NumLock"
    )
    parser_list_devices.set_defaults(func=list_devices)
    args = parser.parse_args()
    global device_name
    global pre_hook
    global led_force
    global fake_uinput

    _debug("=" * 60)
    _debug("numlockw starting (debug enabled via NUMLOCKW_DEBUG)")
    _debug(f"Action: {args.action}")

    if args.pre_hook is not None:
        pre_hook = args.pre_hook
        _debug(f"Configuration: pre_hook set to '{pre_hook}'")

    if args.device_name is not None:
        device_name = args.device_name
        fake_uinput = False
        _debug(f"Configuration: device_name set to '{device_name}'")
        _debug(f"Configuration: fake_uinput disabled (using real device)")

    if args.force_led:
        led_force = True
        _debug(f"Configuration: force_led enabled")

    if args.no_fake_uinput:
        fake_uinput = False
        _debug(f"Configuration: fake_uinput disabled via --no-fake-uinput")

    _debug(f"Final configuration: device_name={device_name!r}, fake_uinput={fake_uinput}, led_force={led_force}, pre_hook={pre_hook!r}")
    _debug("-" * 60)

    # Call the function set by set_defaults in subparser
    _debug(f"Executing action: {args.action}")
    args.func()
    _debug(f"Action '{args.action}' completed successfully")
    _debug("=" * 60)


if __name__ == "__main__":
    main()
