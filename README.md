# NUMLOCKW

A Wayland Clone of `numlockx`

## Install

To install `NUMLOCKW`, use the following command:

```sh
pipx install git+https://github.com/xz-dev/numlockw.git
```

You can then check the available commands with:

```sh
❯ numlockw --help
usage: __main__.py [-h] {on,off,toggle,status}

numlockw is a program to control the NumLock key inside X11 session scripts.

positional arguments:
  {on,off,toggle,status}

options:
  -h, --help            show this help message and exit
```

## Background

1. **Why create it?**
    - `River` does not enable Num Lock at boot.
    - We do not have `numlockx` available for Wayland.

2. **Why not use the wlroots protocol?**
    - The functionality of the protocol depends on its implementation by the compositor.

## Issues

> Why should it work?
> https://wiki.archlinux.org/title/Activating_numlock_on_bootup

I have tested `NUMLOCKW` on TTY and Wayland, and everything is working fine. However, there are some issues that require attention from the compositor developers:

- **Hyprland**: Does not work at all.
- **River**: Works, but avoid using multiple keyboards simultaneously (you can plug them in at the same time, but do not use them concurrently).


## Contributing

We warmly welcome contributions from the community. If you find any bugs or have suggestions for improvements, please feel free to [open an issue](https://github.com/xz-dev/numlockw/issues/new/choose).

You're also encouraged to submit pull requests to help make this project better. If you find this project useful, please consider giving it a :star: to show your support!

Thank you for your interest and contributions! :heart:

