#!/usr/bin/env python3

from typing import List, Optional
from argparse import ArgumentParser

import evdev
from evdev import UInput, InputEvent
from evdev.ecodes import KEY_NUMLOCK, LED_NUML, EV_KEY


def _check_device_has_numlock(device: evdev.InputDevice) -> bool:
    cap = device.capabilities()
    return EV_KEY in cap and KEY_NUMLOCK in cap[EV_KEY]


def _devices() -> List[evdev.InputDevice]:
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    devices = [device for device in devices if _check_device_has_numlock(device)]
    return devices


def numlock_switch():
    ev = InputEvent(1334414993, 274296, EV_KEY, KEY_NUMLOCK, 1)
    with UInput() as ui:
       ui.write_event(ev)
       ui.syn()


def numlock_led_switch(device: evdev.InputDevice, status: bool):
    device.set_led(LED_NUML, 1 if status else 0)


# https://stackoverflow.com/questions/13129804/python-how-to-get-current-keylock-status
def numlock_get_status(devices: List[evdev.InputDevice]) -> bool:
    for device in devices:
        if LED_NUML in device.leds():
            return True
    return False


def toggle(target_status: Optional[bool] = None):
    devices =  _devices()
    status = numlock_get_status(devices)
    if target_status is not None and target_status == status:
        return
    numlock_switch()
    for device in devices:
        numlock_led_switch(device, not status)


def on():
    toggle(True)


def off():
    toggle(False)


def status():
    devices =  _devices()
    print("NumLock is", "on" if numlock_get_status(devices) else "off")


def main():
    parser = ArgumentParser(description="numlockw is a program to control the NumLock key, designed for use with Wayland and tty environments.")
    subparsers = parser.add_subparsers(
        title="actions",
        description="valid actions",
        help="action to perform on NumLock",
        dest="action"
    )
    subparsers.required = True
    parser_on = subparsers.add_parser('on', help="Turn NumLock on")
    parser_on.set_defaults(func=on)
    parser_off = subparsers.add_parser('off', help="Turn NumLock off")
    parser_off.set_defaults(func=off)
    parser_toggle = subparsers.add_parser('toggle', help="Toggle NumLock")
    parser_toggle.set_defaults(func=toggle)
    parser_status = subparsers.add_parser('status', help="Display NumLock status")
    parser_status.set_defaults(func=status)
    args = parser.parse_args()
    parser.add_argument("action", choices=["on", "off", "toggle", "status"])
    args = parser.parse_args()
    args.func()


if __name__ == "__main__":
    main()
