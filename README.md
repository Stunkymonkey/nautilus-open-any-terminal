# nautilus-open-any-terminal

[![Downloads](https://pepy.tech/badge/nautilus-open-any-terminal)](https://pepy.tech/project/nautilus-open-any-terminal)[![Packaging status](https://repology.org/badge/tiny-repos/nautilus-open-any-terminal.svg)](https://repology.org/project/nautilus-open-any-terminal/versions)

is an extension for nautilus, which adds an context-entry for opening other terminal emulators than `gnome-terminal`.

## Supported Terminal Emulators

Right now the plugin is limited to these terminal emulators. If one is missing please open an issue.

- `alacritty`
- `blackbox`
- `cool-retro-term`
- `deepin-terminal`
- `foot`/`footclient`
- `gnome-terminal`
- `guake`
- `hyper`
- `kermit`
- `kgx` (GNOME Console)
- `kitty`
- `konsole`
- `mate-terminal`
- `mlterm`
- `qterminal`
- `sakura`
- `st` [properly patched](https://st.suckless.org/patches/workingdir/)
- `tabby`
- `terminator`
- `terminology`
- `termite`
- `tilix`
- `urxvt`
- `urxvtc`
- `wezterm`
- `xfce4-terminal`

## Installing

### From the AUR (Arch Linux) [![AUR  package](https://repology.org/badge/version-for-repo/aur/nautilus-open-any-terminal.svg)](https://repology.org/project/nautilus-open-any-terminal/versions)

```bash
yay -S nautilus-open-any-terminal
```

### Nixpkgs (NixOS) [![nixpkgs unstable package](https://repology.org/badge/version-for-repo/nix_unstable/nautilus-open-any-terminal.svg)](https://repology.org/project/nautilus-open-any-terminal/versions)

```bash
nix-env -iA nixos.nautilus-open-any-terminal
```

### From PYPI [![PyPI package](https://repology.org/badge/version-for-repo/pypi/nautilus-open-any-terminal.svg)](https://repology.org/project/nautilus-open-any-terminal/versions)

Dependency to install before: `nautilus-python` (`python-nautilus`/`python3-nautilus`(newer) package on Debian / Ubuntu)

User install:

```bash
pip install --user nautilus-open-any-terminal
```

System-wide install:

```bash
pip install nautilus-open-any-terminal
```

### restart nautilus

Then kill Nautilus to allow it to load the new extension:

```bash
nautilus -q
```

If it does not work, try using the following command (from this repository):

```bash
./tools/update-extension-user.sh install    # for a user install
sudo tools/update-extension-system.sh install  # for a system-wide install
```

## Settings

To configure the plugin’s behaviour make sure to run (system-wide):

```bash
glib-compile-schemas /usr/share/glib-2.0/schemas
```

or for (user-wide) installation:

```bash
glib-compile-schemas ~/.local/share/glib-2.0/schemas/
```

### via dconf-editor

![dconf-editor](dconf.png)

### via command-line

```bash
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal terminal alacritty
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal keybindings '<Ctrl><Alt>t'
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal new-tab true
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal flatpak system
```

## Uninstall

since `setup.py` does not provide a natively uninstall method the scripts have an uninstall option.

```bash
./tools/update-extension-user.sh uninstall    # for a user uninstall
sudo tools/update-extension-system.sh uninstall  # for a system-wide uninstall
```
