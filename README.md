# nautilus-open-any-terminal

[![Downloads](https://pepy.tech/badge/nautilus-open-any-terminal)](https://pepy.tech/project/nautilus-open-any-terminal)[![Packaging status](https://repology.org/badge/tiny-repos/nautilus-open-any-terminal.svg)](https://repology.org/project/nautilus-open-any-terminal/versions)

is an extension for nautilus, which adds an context-entry for opening other editor then `gnome-terminal`.

## Supported Terminal-Emulators

Right now the plugin is limited to these terminal-emulators. If one is missing please open an issue.

- `alacritty`
- `cool-retro-term`
- `deepin-terminal`
- `gnome-terminal`
- `guake`
- `hyper`
- `kitty`
- `konsole`
- `mate-terminal`
- `mlterm`
- `qterminal`
- `st` [properly patched](https://st.suckless.org/patches/workingdir/)
- `terminator`
- `terminology`
- `termite`
- `tilix`
- `urxvt`
- `xfce4-terminal`

## Installing

### From the AUR (Arch Linux) [![AUR  package](https://repology.org/badge/version-for-repo/aur/nautilus-open-any-terminal.svg)](https://repology.org/project/nautilus-open-any-terminal/versions)

```bash
yay -S nautilus-open-any-terminal
```

### From PYPI

Dependency to install before: `nautilus-python` (`python-nautilus` package on Debian / Ubuntu)

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
sudo tools/update-extension-user.sh install    # for a user install
sudo tools/update-extension-system.sh install  # for a system-wide install
```

## Settings

### via dconf-editor

![](dconf.png)

### via commandline

```bash
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal terminal alacritty
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal keybindings '<Ctrl><Alt>t'
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal new-tab true
```
