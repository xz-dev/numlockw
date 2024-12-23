#!/usr/bin/env python3

import time
from argparse import ArgumentParser
from typing import List, Optional

import evdev
from evdev import UInput
from evdev.ecodes import EV_KEY, EV_SYN, KEY_NUMLOCK, LED_NUML, SYN_REPORT

UINPOUT_DEVICE_NAME = "numlockw-evdev-uinput"

DEBUG = False

device_name = None
pre_hook = None
led_force = False
fake_uinput = True


def eprint(text):
    if not DEBUG:
        return
    import logging

    logging.warning(text)


def _check_device_has_numlock(device: evdev.InputDevice) -> bool:
    cap = device.capabilities()
    return EV_KEY in cap and KEY_NUMLOCK in cap[EV_KEY]


def _devices(device_name: Optional[str]) -> List[evdev.InputDevice]:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    devices = [device for device in devices if _check_device_has_numlock(device)]
    if device_name is None:
        return devices[:1]
    elif device_name == "*":
        return devices
    else:
        return [device for device in devices if device.name == device_name]


def numlock_switch(devices: List[evdev.InputDevice] = None):
    if fake_uinput:
        devices = [UInput(name=UINPOUT_DEVICE_NAME)]
    else:
        devices = devices
    for ui in devices:
        if pre_hook is not None:
            import subprocess

            command_str = pre_hook.replace("${{udevice}}", ui.name)
            subprocess.run(command_str, shell=True)
        ui.write(EV_KEY, KEY_NUMLOCK, 1)
        ui.write(EV_SYN, SYN_REPORT, 0)
        time.sleep(0.05)  # 50ms, avoid GNOME key debounce
        ui.write(EV_KEY, KEY_NUMLOCK, 0)
        ui.write(EV_SYN, SYN_REPORT, 0)
        ui.close()


def numlock_led_switch(devices: List[evdev.InputDevice], status: bool):
    for device in devices:
        try:
            device.set_led(LED_NUML, 1 if status else 0)
        except Exception:
            eprint(f"Error setting LED status for device {device.name}")
            import traceback

            eprint(f"Error: {traceback.format_exc()}")


# https://stackoverflow.com/questions/13129804/python-how-to-get-current-keylock-status
def numlock_get_status(device: evdev.InputDevice) -> Optional[bool]:
    try:
        return LED_NUML in device.leds()
    except Exception:
        eprint(f"Error getting LED status for device {device.name}")
        import traceback

        eprint(f"Error: {traceback.format_exc()}")
        return None


def numlock_get_status_devices(devices: List[evdev.InputDevice]) -> bool:
    for device in devices:
        if numlock_get_status(device):
            return True
    return False


def toggle(target_status: Optional[bool] = None):
    devices = _devices(device_name)
    status = numlock_get_status_devices(devices)
    if target_status is not None and target_status == status:
        return
    numlock_switch(devices)
    if led_force:
        numlock_led_switch(devices, not status)


def on():
    toggle(True)


def off():
    toggle(False)


def status():
    devices = _devices("*" if device_name is None else device_name)
    print("NumLock is", "on" if numlock_get_status_devices(devices) else "off")


def list_devices():
    with UInput(name=UINPOUT_DEVICE_NAME):
        devices = _devices("*" if device_name is None else device_name)
        print("Path | Device Name | Physical Topology | LED Status")
        for device in devices:
            led_status = numlock_get_status(device)
            print(
                device.path,
                device.name,
                device.phys,
                "N/A" if led_status is None else "ON" if led_status else "OFF",
                sep=" | ",
            )


def main():
    parser = ArgumentParser(
        description="numlockw is a program to control the NumLock key, designed for use with Wayland and tty environments."
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
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
    global DEBUG
    global device_name
    global pre_hook
    global led_force
    global fake_uinput

    DEBUG = args.debug
    if DEBUG:
        print("Debug mode enabled")
    if args.pre_hook is not None:
        pre_hook = args.pre_hook
    if args.device_name is not None:
        device_name = args.device_name
        fake_uinput = False
    if args.force_led:
        led_force = True
    if args.no_fake_uinput:
        fake_uinput = False
    # Call the function set by set_defaults in subparser
    args.func()


if __name__ == "__main__":
    main()
