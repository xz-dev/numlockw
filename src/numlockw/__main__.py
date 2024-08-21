#!/usr/bin/env python3

from typing import List, Optional
from argparse import ArgumentParser

import evdev
from evdev import UInput, InputEvent
from evdev.ecodes import KEY_NUMLOCK, LED_NUML, EV_KEY


device_name = None
pre_hook = None
led_only = False

DEBUG = False


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
    if device_name is not None:
        devices = [device for device in devices if device.name == device_name]
        if not devices:
            raise ValueError(f"Device with name {device_name} not found")
    return devices


def numlock_switch():
    ev = InputEvent(1334414993, 274296, EV_KEY, KEY_NUMLOCK, 1)
    with UInput() as ui:
        if pre_hook is not None:
            import subprocess
            command_str = pre_hook.replace("${{udevice}}", ui.name)
            subprocess.run(command_str, shell=True)
        ui.write_event(ev)
        ui.syn()


def numlock_led_switch(device: evdev.InputDevice, status: bool):
    try:
        device.set_led(LED_NUML, 1 if status else 0)
    except Exception:
        eprint(f"Error setting LED status for device {device.name}")
        import traceback
        eprint(f"Error: {traceback.format_exc()}")


# https://stackoverflow.com/questions/13129804/python-how-to-get-current-keylock-status
def numlock_get_status(devices: List[evdev.InputDevice]) -> bool:
    for device in devices:
        try:
            if LED_NUML in device.leds():
                return True
        except Exception:
            eprint(f"Error getting LED status for device {device.name}")
            import traceback
            eprint(f"Error: {traceback.format_exc()}")
    return False


def toggle(target_status: Optional[bool] = None):
    devices = _devices(device_name)
    status = numlock_get_status(devices)
    if target_status is not None and target_status == status:
        return
    if not led_only:
        numlock_switch()
    for device in devices:
        numlock_led_switch(device, not status)


def on():
    toggle(True)


def off():
    toggle(False)


def status():
    devices = _devices(device_name)
    print("NumLock is", "on" if numlock_get_status(devices) else "off")


def list_devices():
    devices = _devices(None)
    print("Path | Device Name | Physical Topology")
    for device in devices:
        print(device.path, device.name, device.phys, sep=" | ")


def main():
    parser = ArgumentParser(description="numlockw is a program to control the NumLock key, designed for use with Wayland and tty environments.")
    parser.add_argument('--debug', action="store_true", help="Enable debug output")
    parser.add_argument('--device-name', type=str, default=None, help="The name of the input device to use. If not provided, will fake keyboard to enable NumLock, and enable LDE_NUML on all devices that support it.")
    parser.add_argument("--pre-hook", type=str, default=None, help="A command to run when NumLock is toggled. The command will be run with the status of uinput device name ${{udevice}}.")
    parser.add_argument("--led-only", action="store_true", help="Only toggle the LED, do not send key event.")
    subparsers = parser.add_subparsers(
        title="actions",
        description="valid actions",
        help="action to perform on NumLock",
        dest="action"
    )
    subparsers.required = True
    # Add parsers for each command
    parser_on = subparsers.add_parser('on', help="Turn NumLock on")
    parser_on.set_defaults(func=on)
    parser_off = subparsers.add_parser('off', help="Turn NumLock off")
    parser_off.set_defaults(func=off)
    parser_toggle = subparsers.add_parser('toggle', help="Toggle NumLock")
    parser_toggle.set_defaults(func=toggle)
    parser_status = subparsers.add_parser('status', help="Display NumLock status")
    parser_status.set_defaults(func=status)
    parser_list_devices = subparsers.add_parser('list-devices', help="List devices that support NumLock")
    parser_list_devices.set_defaults(func=list_devices)
    args = parser.parse_args()
    global DEBUG
    DEBUG = args.debug
    if DEBUG:
        print("Debug mode enabled")
    if args.pre_hook is not None:
        global pre_hook
        pre_hook = args.pre_hook
    if args.device_name is not None:
        global device_name
        device_name = args.device_name
    if args.led_only:
        global led_only
        led_only = True
    # Call the function set by set_defaults in subparser
    args.func()


if __name__ == "__main__":
    main()
