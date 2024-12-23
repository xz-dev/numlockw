# NumLockW

A Wayland Clone of `numlockx`

## Install

To install `numlockw`, use the following commands:

```sh
sudo usermod -a -G plugdev $USER  # For Arch users: Refer to https://wiki.archlinux.org/title/Udev#Allowing_regular_users_to_use_devices
pipx install git+https://github.com/xz-dev/numlockw.git
```

You can then check the available commands with:

```sh
numlockw --help
```

And simply run:
```sh
numlockw on
```

Example output:

```
usage: numlockw [-h] [--debug] [--device-name DEVICE_NAME] [--no-fake-uinput] [--pre-hook PRE_HOOK] [--force-led]
                {on,off,toggle,status,list-devices} ...

numlockw is a program to control the NumLock key, designed for use with Wayland and tty environments.

options:
  -h, --help            show this help message and exit
  --debug               Enable debug output
  --device-name DEVICE_NAME
                        The name of the input device to use. If not provided, will fake keyboard to enable NumLock, and enable LDE_NUML on all
                        devices that support it.
  --no-fake-uinput      Do not fake uinput device, use real devices
  --pre-hook PRE_HOOK   A command to run when NumLock is toggled. The command will be run with the status of uinput device name ${{udevice}}.
  --force-led           Force setting LED_NUML on all devices that support it, not dependent system to set it.

actions:
  valid actions

  {on,off,toggle,status,list-devices}
                        action to perform on NumLock
    on                  Turn NumLock on
    off                 Turn NumLock off
    toggle              Toggle NumLock
    status              Display NumLock status
    list-devices        List devices that support NumLock
```

## Use Notes

1. Sometimes, you might need some operation before "Click" NumLock. You can try --pre-hook

```sh
numlockw --pre-hook 'echo ${{udevice}}' on  # Print uinput (Fake keyboard) device name
```

2. Choice exist(real) keyboard to "Click" NumLock:
```sh
numlockw --device-name 'AT Translated Set 2 keyboard' on
```

3. If you want to **Force** enable/disable LED with switch NumLock by some reason:

```sh
numlockw list-devices
numlockw --device-name 'AT Translated Set 2 keyboard' --force-led on  # Only for 'AT Translated Set 2 keyboard'
```

## Background

### Why create it?

- **River**: Does not enable Num Lock at boot.
- `numlockx` is not available for Wayland.

### Why not use the wlroots protocol?

- The functionality of the protocol depends on its implementation by the compositor.

### Why should it work?

Refer to the [Activating NumLock on Bootup - ArchWiki](https://wiki.archlinux.org/title/Activating_numlock_on_bootup) for background information.

## Issues

1. **Sync status on LED and actual state**:
   - The method described [here](https://stackoverflow.com/questions/13129804/python-how-to-get-current-keylock-status) seems problematic, but no better solution was found.

2. **Is it working?** (welcome add more):
   - I have tested `NumLockW` on TTY, KDE (Wayland) and Hyprland, and everything is working fine. However, there are some issues that require attention from the compositor developers:
     - **River**: Work, but avoid using `Alt` or `Ctrl` with multiple keyboards simultaneously (you can plug them in at the same time, but do not use them concurrently, it's a bug of `River`).
     - **GNOME**: Work, but you must choice an exist keyboard, like: `numlockw --device-name 'AT Translated Set 2 keyboard' on`

## Contributing

We warmly welcome contributions from the community. If you find any bugs or have suggestions for improvements, please feel free to [open an issue](https://github.com/xz-dev/numlockw/issues/new/choose).

You're also encouraged to submit pull requests to help make this project better. If you find this project useful, please consider giving it a :star: to show your support!

Thank you for your interest and contributions! :heart:

