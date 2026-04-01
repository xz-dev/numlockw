# evdev-holder

A lightweight daemon that prevents LED pulsing on certain hardware (e.g. Tuxedo Stellaris 15 Gen3) by keeping evdev input device file descriptors permanently open.

Pure Python. No external dependencies.

## Problem

On affected hardware, every time a program opens and closes an `/dev/input/event*` device, the kernel re-asserts LED states to the embedded controller. The firmware interprets this as a state transition, causing a visible LED pulse. Tools like `numlockw status` that poll at 1-2 Hz make the touchpad LED flash constantly.

Kernel call chain on every `open()` when no other fd is held:

```
open("/dev/input/eventX")
  → evdev_open_device()        # evdev->open goes 0 → 1
  → input_open_device()        # dev->users goes 0 → 1
  → dev->open()                # hardware driver callback
  → e.g. hidinput_open() → hid_hw_open() → transport layer reinit
  → EC firmware pulses LED (hardware/firmware-specific side effect)
```

## Solution

This daemon holds at least one fd open per device. With `evdev->open` permanently >= 1, subsequent opens skip `input_open_device()` entirely, and LEDs are never re-asserted.

## Usage

### Run directly

```bash
sudo python3 evdev_holder.py
```

Options:

| Flag | Description |
|------|-------------|
| `--quiet`, `-q` | Only show warnings and errors |
| `--interval N` | Device rescan interval in seconds (default: 5) |

### Install as systemd service

```bash
# Copy the script
sudo mkdir -p /opt/evdev-holder
sudo cp evdev_holder.py /opt/evdev-holder/

# Install and enable the service
sudo cp evdev-holder.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now evdev-holder
```

Check status:

```bash
sudo systemctl status evdev-holder
```

### Uninstall

```bash
sudo systemctl disable --now evdev-holder
sudo rm /etc/systemd/system/evdev-holder.service
sudo rm -rf /opt/evdev-holder
sudo systemctl daemon-reload
```

## See also

- [Reddit report](https://www.reddit.com/r/tuxedocomputers/comments/1rtj3c9/numlockw_status_causes_touchpad_led_to_pulse/)

