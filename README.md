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

Example output:

```
usage: numlockw [-h] [--device-name DEVICE_NAME] [--pre-hook PRE_HOOK] [--led-only]
                {on,off,toggle,status,list-devices} ...

numlockw is a program to control the NumLock key, designed for use with Wayland and tty
environments.

options:
  -h, --help            show this help message and exit
  --device-name DEVICE_NAME
                        The name of the input device to use. If not provided, will fake keyboard to
                        enable NumLock, and enable LDE_NUML on all devices that support it.
  --pre-hook PRE_HOOK   A command to run when NumLock is toggled. The command will be run with the
                        status of uinput device name ${{udevice}}.
  --led-only            Only toggle the LED, do not send key event.

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

``` sh
numlockw --pre-hook 'echo ${{udevice}}' on  # Print uinput (Fake keyboard) device name
```

2. If you only want to enable/disable LED by some reason:

``` sh
numlockw list-devices
numlockw --led-only off  # For all device
numlockw --device-name 'AT Translated Set 2 keyboard' --led-only off  # Only for 'AT Translated Set 2 keyboard'
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

2. **Is it working?**:
   - I have tested `NumLockW` on TTY and KDE (Wayland), and everything is working fine. However, there are some issues that require attention from the compositor developers:
     - **Hyprland**: Does not work at all (including LED).
     - **River**: Works, but avoid using `Alt` or `Ctrl` with multiple keyboards simultaneously (you can plug them in at the same time, but do not use them concurrently, it's a bug of `River`).
     - **GNOME**: Does not fully work (LED works); no real function, LED is buggy similar to `River`.

## Contributing

We warmly welcome contributions from the community. If you find any bugs or have suggestions for improvements, please feel free to [open an issue](https://github.com/xz-dev/numlockw/issues/new/choose).

You're also encouraged to submit pull requests to help make this project better. If you find this project useful, please consider giving it a :star: to show your support!

Thank you for your interest and contributions! :heart:

