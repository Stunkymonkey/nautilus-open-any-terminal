"""nautilus extension: nautilus_open_any_terminal"""

# based on: https://github.com/gnunn1/tilix/blob/master/data/nautilus/open-tilix.py

import ast
import re
import shlex
from dataclasses import dataclass, field
from functools import cache
from gettext import gettext, translation
from os.path import expanduser
from subprocess import Popen
from typing import Optional

try:
    from urllib import unquote  # type: ignore

    from urlparse import urlparse
except ImportError:
    from urllib.parse import unquote, urlparse

from gi import get_required_version, require_version

API_VERSION: str
if (API_VERSION := get_required_version("Nautilus")) is not None:
    try:
        require_version("Gtk", "4.0")
    except ValueError:
        require_version("Gtk", "3.0")
    from gi.repository import Nautilus as FileManager
elif (API_VERSION := get_required_version("Caja")) is not None:
    require_version("Gtk", "3.0")
    from gi.repository import Caja as FileManager
else:
    raise RuntimeError("This module can only be executed as a Nautilus/Caja extension")

from gi.repository import Gio, GObject, Gtk  # noqa: E402 pylint: disable=wrong-import-position


@dataclass(frozen=True)
class Terminal:
    """Data class representing a terminal configuration."""

    name: str
    workdir_arguments: Optional[list[str]] = None
    new_tab_arguments: Optional[list[str]] = None
    new_window_arguments: Optional[list[str]] = None
    command_arguments: list[str] = field(default_factory=lambda: ["-e"])
    flatpak_package: Optional[str] = None


TERMINALS = {
    "alacritty": Terminal("Alacritty"),
    "blackbox": Terminal(
        "Black Box",
        workdir_arguments=["--working-directory"],
        command_arguments=["-c"],
        flatpak_package="com.raggesilver.BlackBox",
    ),
    "cool-retro-term": Terminal("cool-retro-term", workdir_arguments=["--workdir"]),
    "deepin-terminal": Terminal("Deepin Terminal"),
    "foot": Terminal("Foot"),
    "footclient": Terminal("FootClient"),
    "gnome-terminal": Terminal("Terminal", new_tab_arguments=["--tab"]),
    "guake": Terminal("Guake", workdir_arguments=["--show", "--new-tab"]),
    "hyper": Terminal("Hyper"),
    "kermit": Terminal("Kermit"),
    "kgx": Terminal("Console", new_tab_arguments=["--tab"]),
    "kitty": Terminal("kitty"),
    "konsole": Terminal("Konsole", new_tab_arguments=["--new-tab"]),
    "mate-terminal": Terminal("Mate Terminal", new_tab_arguments=["--tab"]),
    "mlterm": Terminal("Mlterm"),
    "ptyxis": Terminal(
        "Ptyxis",
        workdir_arguments=["-d"],
        command_arguments=["-x"],
        new_tab_arguments=["--tab"],
        new_window_arguments=["--new-window"],
        flatpak_package="org.gnome.Ptyxis",
    ),
    "ptyxis-nightly": Terminal(
        "Ptyxis",
        workdir_arguments=["-d"],
        command_arguments=["-x"],
        new_tab_arguments=["--tab"],
        new_window_arguments=["--new-window"],
        flatpak_package="org.gnome.Ptyxis.Devel",
    ),
    "qterminal": Terminal("QTerminal"),
    "rio": Terminal("Rio"),
    "sakura": Terminal("Sakura"),
    "st": Terminal("Simple Terminal"),
    "tabby": Terminal("Tabby", command_arguments=["run"], workdir_arguments=["open"]),
    "terminator": Terminal("Terminator", new_tab_arguments=["--new-tab"]),
    "terminology": Terminal("Terminology"),
    "terminus": Terminal("Terminus"),
    "termite": Terminal("Termite"),
    "tilix": Terminal("Tilix", flatpak_package="com.gexperts.Tilix"),
    "urxvt": Terminal("rxvt-unicode"),
    "urxvtc": Terminal("urxvtc"),
    "uxterm": Terminal("UXTerm"),
    "warp": Terminal("warp"),
    "wezterm": Terminal(
        "Wez's Terminal Emulator",
        workdir_arguments=["start", "--cwd"],
        flatpak_package="org.wezfurlong.wezterm",
    ),
    "xfce4-terminal": Terminal("Xfce Terminal", new_tab_arguments=["--tab"]),
    "xterm": Terminal("XTerm"),
}

FLATPAK_PARMS = ["off", "system", "user"]

terminal = "gnome-terminal"
terminal_cmd: list[str] = None  # type: ignore
terminal_data: Terminal = TERMINALS["gnome-terminal"]
new_tab = False
flatpak = FLATPAK_PARMS[0]

GSETTINGS_PATH = "com.github.stunkymonkey.nautilus-open-any-terminal"
GSETTINGS_KEYBINDINGS = "keybindings"
GSETTINGS_BIND_REMOTE = "bind-remote"
GSETTINGS_TERMINAL = "terminal"
GSETTINGS_NEW_TAB = "new-tab"
GSETTINGS_FLATPAK = "flatpak"
REMOTE_URI_SCHEME = ["ftp", "sftp"]

_ = gettext
for localedir in [expanduser("~/.local/share/locale"), "/usr/share/locale"]:
    try:
        trans = translation("nautilus-open-any-terminal", localedir)
        trans.install()
        _ = trans.gettext
        break
    except FileNotFoundError:
        continue


# Adapted from https://www.freedesktop.org/software/systemd/man/latest/os-release.html
def read_os_release():
    """Read and parse the OS release information."""
    possible_os_release_paths = ["/etc/os-release", "/usr/lib/os-release"]
    for file_path in possible_os_release_paths:
        try:
            with open(file_path, mode="r", encoding="utf-8") as os_release:
                for line_number, line in enumerate(os_release, start=1):
                    line = line.rstrip()
                    if not line or line.startswith("#"):
                        continue
                    result = re.match(r"([A-Z][A-Z_0-9]+)=(.*)", line)
                    if result:
                        name, val = result.groups()
                        if val and val[0] in "\"'":
                            val = ast.literal_eval(val)
                        yield name, val
                    else:
                        raise OSError(f"{file_path}:{line_number}: bad line {line!r}")
        except FileNotFoundError:
            continue


@cache
def distro_id() -> set[str]:
    """get the set of distribution ids"""
    try:
        os_release = dict(read_os_release())
    except OSError:
        return set(["unknown"])
    ids = [os_release["ID"]]
    if id_like := os_release.get("ID_LIKE"):
        ids.extend(id_like.split(" "))
    return set(ids)


def open_remote_terminal_in_uri(uri: str):
    """Open a new remote terminal"""
    result = urlparse(uri)
    cmd = terminal_cmd.copy()

    cmd.extend(terminal_data.command_arguments)
    cmd.extend(["ssh", "-t"])
    if result.username:
        cmd.append(f"{result.username}@{result.hostname}")
    else:
        cmd.append(result.hostname)

    if result.port:
        cmd.append("-p")
        cmd.append(str(result.port))

    cmd.extend(["cd", shlex.quote(unquote(result.path)), ";", "exec", "-a", "-$SHELL", "$SHELL"])

    Popen(cmd)  # pylint: disable=consider-using-with


def open_local_terminal_in_uri(uri: str):
    """open the new terminal with correct path"""
    result = urlparse(uri)
    cmd = terminal_cmd.copy()
    if terminal == "warp":
        Popen(  # pylint: disable=consider-using-with
            ["xdg-open", f'warp://action/new_{"tab" if new_tab else "window"}?path={result.path}']
        )
        return

    filename = unquote(result.path)
    if new_tab and terminal_data.new_tab_arguments:
        cmd.extend(terminal_data.new_tab_arguments)
    elif terminal_data.new_window_arguments:
        cmd.extend(terminal_data.new_window_arguments)

    if filename and terminal_data.workdir_arguments:
        cmd.extend(terminal_data.workdir_arguments)
        cmd.append(filename)

    Popen(cmd, cwd=filename)  # pylint: disable=consider-using-with


def menu_item_id(*, foreground: bool, remote: bool):
    return f"OpenTerminal::open{'_' if foreground else '_bg_'}{'remote' if remote else 'file'}_item"


def get_menu_items(file: FileManager.FileInfo, callback, foreground: bool):
    items = []
    remote = file.get_uri_scheme() in REMOTE_URI_SCHEME

    if remote:
        if foreground:
            REMOTE_LABEL = _("Open In Remote {}")
            REMOTE_TIP = _("Open Remote {} In {}")
            LOCAL_LABEL = _("Open In Local {}")
            LOCAL_TIP = _("Open Local {} In {}")
            tip = REMOTE_TIP.format(terminal_data.name, file.get_name())
        else:
            REMOTE_LABEL = _("Open Remote {} Here")
            REMOTE_TIP = _("Open Remote {} In This Directory")
            LOCAL_LABEL = _("Open Local {} Here")
            LOCAL_TIP = _("Open Local {} In This Directory")
            tip = REMOTE_TIP.format(terminal_data.name)

        item = FileManager.MenuItem(
            name=menu_item_id(foreground=foreground, remote=True),
            label=REMOTE_LABEL.format(terminal_data.name),
            tip=tip,
        )
        item.connect("activate", callback, file, True)
        items.append(item)
    elif foreground:
        LOCAL_LABEL = _("Open In {}")
        LOCAL_TIP = _("Open {} In {}")
    else:
        LOCAL_LABEL = _("Open {} Here")
        LOCAL_TIP = _("Open {} In This Directory")

    # Let wezterm handle opening a local terminal
    if terminal == "wezterm" and flatpak == "off":
        return items

    if foreground:
        tip = LOCAL_TIP.format(terminal_data.name, file.get_name())
    else:
        tip = LOCAL_TIP.format(terminal_data.name)

    item = FileManager.MenuItem(
        name=menu_item_id(foreground=foreground, remote=False),
        label=LOCAL_LABEL.format(terminal_data.name),
        tip=tip,
    )
    item.connect("activate", callback, file, False)
    items.append(item)
    return items


def set_terminal_args(*_args):
    """set the terminal_cmd to the correct values"""
    global new_tab
    global flatpak
    global terminal_cmd
    global terminal_data
    value = _gsettings.get_string(GSETTINGS_TERMINAL)
    newer_tab = _gsettings.get_boolean(GSETTINGS_NEW_TAB)
    flatpak = FLATPAK_PARMS[_gsettings.get_enum(GSETTINGS_FLATPAK)]
    new_terminal_data = TERMINALS.get(value)
    if not new_terminal_data:
        print(f'open-any-terminal: unknown terminal "{value}"')
        return

    global terminal
    terminal = value
    terminal_data = new_terminal_data
    if newer_tab and terminal_data.new_tab_arguments:
        new_tab = newer_tab
        new_tab_text = "opening in a new tab"
    else:
        new_tab_text = "opening a new window"
    if newer_tab and not terminal_data.new_tab_arguments:
        new_tab_text += " (terminal does not support tabs)"
    if flatpak != FLATPAK_PARMS[0] and terminal_data.flatpak_package is not None:
        terminal_cmd = ["flatpak", "run", "--" + flatpak, terminal_data.flatpak_package]
        flatpak_text = f"with flatpak as {flatpak}"
    else:
        terminal_cmd = [terminal]
        if terminal == "blackbox" and "fedora" in distro_id():
            # It's called like this on fedora
            terminal_cmd[0] = "blackbox-terminal"
        flatpak = FLATPAK_PARMS[0]
        flatpak_text = ""
    print(f'open-any-terminal: terminal is set to "{terminal}" {new_tab_text} {flatpak_text}')


if API_VERSION in ("3.0", "2.0"):

    class OpenAnyTerminalShortcutProvider(GObject.GObject, FileManager.LocationWidgetProvider):
        """Provide keyboard shortcuts for opening terminals in Nautilus."""

        def __init__(self):
            gsettings_source = Gio.SettingsSchemaSource.get_default()
            if gsettings_source.lookup(GSETTINGS_PATH, True):
                self._gsettings = Gio.Settings.new(GSETTINGS_PATH)
                self._gsettings.connect("changed", self._bind_shortcut)
                self._create_accel_group()
            self._window = None
            self._uri = None

        def _create_accel_group(self):
            self._accel_group = Gtk.AccelGroup()
            shortcut = self._gsettings.get_string(GSETTINGS_KEYBINDINGS)
            key, mod = Gtk.accelerator_parse(shortcut)
            self._accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, self._open_terminal)

        def _bind_shortcut(self, _gsettings, key):
            if key == GSETTINGS_KEYBINDINGS:
                self._accel_group.disconnect(self._open_terminal)
                self._create_accel_group()

        def _open_terminal(self, *_args):
            if _gsettings.get_boolean(GSETTINGS_BIND_REMOTE):
                open_local_terminal_in_uri(self._uri)
            else:
                open_remote_terminal_in_uri(self._uri)

        def get_widget(self, uri, window):
            """follows uri and sets the correct window"""
            self._uri = uri
            if self._window:
                self._window.remove_accel_group(self._accel_group)
            if self._gsettings:
                window.add_accel_group(self._accel_group)
            self._window = window


class OpenAnyTerminalExtension(GObject.GObject, FileManager.MenuProvider):
    """Provide context menu items for opening terminals in Nautilus."""

    def _menu_activate_cb(self, menu, file_, remote: bool):
        if remote:
            open_remote_terminal_in_uri(file_.get_uri())
        else:
            open_local_terminal_in_uri(file_.get_location().get_path())

    def get_file_items(self, *args):
        """Generates a list of menu items for a file or folder in the Nautilus file manager."""
        # `args` will be `[files: List[Nautilus.FileInfo]]` in Nautilus 4.0 API,
        # and `[window: Gtk.Widget, files: List[Nautilus.FileInfo]]` in Nautilus 3.0 API.

        files = args[-1]

        if len(files) != 1:
            return []
        file_ = files[0]

        if file_.is_directory():
            return get_menu_items(file_, self._menu_activate_cb, True)

        return []

    def get_background_items(self, *args):
        """Generates a list of background menu items for a file or folder in the Nautilus file manager."""
        # `args` will be `[folder: Nautilus.FileInfo]` in Nautilus 4.0 API,
        # and `[window: Gtk.Widget, file: Nautilus.FileInfo]` in Nautilus 3.0 API.

        file_ = args[-1]
        return get_menu_items(file_, self._menu_activate_cb, False)


source = Gio.SettingsSchemaSource.get_default()
if source is not None and source.lookup(GSETTINGS_PATH, True):
    _gsettings = Gio.Settings.new(GSETTINGS_PATH)
    _gsettings.connect("changed", set_terminal_args)
    set_terminal_args()
