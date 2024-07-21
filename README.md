# NUMLOCKW

A Wayland Clone of `numlockx`

``` sh
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

I have tested `NUMLOCKW` on TTY and Wayland, and everything is working fine. However, there are some issues that require attention from the compositor developers:

- **Hyprland**: Does not work at all.
- **River**: Works, but avoid using multiple keyboards simultaneously (you can plug them in at the same time, but do not use them concurrently).
