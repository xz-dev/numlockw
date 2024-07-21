# NUMLOCKW

A Wayland Clone of `numlockx`

## Install

To install `NUMLOCKW`, use the following commands:

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
usage: __main__.py [-h] {on, off, toggle, status}

numlockw is a program to control the NumLock key inside X11 session scripts.

positional arguments:
  {on, off, toggle, status}

options:
  -h, --help            show this help message and exit
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
   - I have tested `NUMLOCKW` on TTY and KDE (Wayland), and everything is working fine. However, there are some issues that require attention from the compositor developers:
     - **Hyprland**: Does not work at all (including LED).
     - **River**: Works, but avoid using `Alt` or `Ctrl` with multiple keyboards simultaneously (you can plug them in at the same time, but do not use them concurrently, it's a bug of `River`).
     - **GNOME**: Does not fully work (LED works); no real function, LED is buggy similar to `River`.

## Contributing

We warmly welcome contributions from the community. If you find any bugs or have suggestions for improvements, please feel free to [open an issue](https://github.com/xz-dev/numlockw/issues/new/choose).

You're also encouraged to submit pull requests to help make this project better. If you find this project useful, please consider giving it a :star: to show your support!

Thank you for your interest and contributions! :heart:

