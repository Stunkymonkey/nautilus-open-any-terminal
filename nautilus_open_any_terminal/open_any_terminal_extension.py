# -*- coding: utf-8 -*-
# based on: https://github.com/gnunn1/tilix/blob/master/data/nautilus/open-tilix.py

import platform
import shlex
from dataclasses import dataclass, field
from functools import cache
from gettext import gettext, translation
from os import environ
from subprocess import Popen

try:
    from urllib import unquote  # type: ignore

    from urlparse import urlparse
except ImportError:
    from urllib.parse import unquote, urlparse

from gi import require_version

try:
    require_version("Gtk", "4.0")
    require_version("Nautilus", "4.0")
except ValueError:
    require_version("Gtk", "3.0")
    require_version("Nautilus", "3.0")

from gi.repository import Gio, GObject, Gtk, Nautilus  # noqa: E402


@dataclass(frozen=True)
class Terminal:
    name: str
    workdir_arguments: list[str] | None = None
    new_tab_arguments: list[str] | None = None
    new_window_arguments: list[str] | None = None
    command_arguments: list[str] = field(default_factory=lambda: ["-e"])
    flatpak_package: str | None = None


TERMINALS = {
    "alacritty": Terminal("Alacritty"),
    "blackbox": Terminal(
        "Black Box",
        workdir_arguments=["--working-directory"],
        command_arguments=["-c"],
        flatpak_package="com.raggesilver.BlackBox",
    ),
    "cool-retro-term": Terminal(
        "cool-retro-term", workdir_arguments=["--workdir", "."]
    ),
    "deepin-terminal": Terminal("Deepin Terminal"),
    "foot": Terminal("Foot"),
    "footclient": Terminal("FootClient"),
    "gnome-terminal": Terminal("Terminal", new_tab_arguments=["--tab"]),
    "guake": Terminal("Guake", workdir_arguments=["--show", "--new-tab=."]),
    "hyper": Terminal("Hyper"),
    "kermit": Terminal("Kermit"),
    "kgx": Terminal("Console", new_tab_arguments=["--tab"]),
    "kitty": Terminal("kitty"),
    "konsole": Terminal("Konsole", new_tab_arguments=["--new-tab"]),
    "mate-terminal": Terminal("Mate Terminal", new_tab_arguments=["--tab"]),
    "mlterm": Terminal("Mlterm"),
    "prompt": Terminal(
        "Prompt",
        command_arguments=["-x"],
        new_tab_arguments=["--tab"],
        new_window_arguments=["--new-window"],
        flatpak_package="org.gnome.Prompt",
    ),
    "qterminal": Terminal("QTerminal"),
    "sakura": Terminal("Sakura"),
    "st": Terminal("Simple Terminal"),
    "terminator": Terminal("Terminator", new_tab_arguments=["--new-tab"]),
    "terminology": Terminal("Terminology"),
    "terminus": Terminal("Terminus"),
    "termite": Terminal("Termite"),
    "tilix": Terminal("Tilix", flatpak_package="com.gexperts.Tilix"),
    "urxvt": Terminal("rxvt-unicode"),
    "urxvtc": Terminal("urxvtc"),
    "uxterm": Terminal("UXTerm"),
    "wezterm": Terminal(
        "Wez's Terminal Emulator",
        workdir_arguments=["start", "--cwd", "."],
        flatpak_package="org.wezfurlong.wezterm",
    ),
    "xfce4-terminal": Terminal("Xfce Terminal", new_tab_arguments=["--tab"]),
    "xterm": Terminal("XTerm"),
    "tabby": Terminal("Tabby", command_arguments=["run"], workdir_arguments=["open"]),
}

FLATPAK_PARMS = ["off", "system", "user"]

global terminal
terminal = "gnome-terminal"
terminal_cmd: list[str] = None  # type: ignore
terminal_data: Terminal = TERMINALS["gnome-terminal"]
new_tab = False
flatpak = FLATPAK_PARMS[0]
GSETTINGS_PATH = "com.github.stunkymonkey.nautilus-open-any-terminal"
GSETTINGS_KEYBINDINGS = "keybindings"
GSETTINGS_TERMINAL = "terminal"
GSETTINGS_NEW_TAB = "new-tab"
GSETTINGS_FLATPAK = "flatpak"
REMOTE_URI_SCHEME = ["ftp", "sftp"]

_ = gettext
for localedir in ["/usr/share/locale", environ["HOME"] + "/.local/share/locale"]:
    try:
        trans = translation("nautilus-open-any-terminal", localedir)
        trans.install()
        _ = trans.gettext
        break
    except FileNotFoundError:
        continue


def _checkdecode(s):
    """Decode string assuming utf encoding if it's bytes, else return unmodified"""
    return s.decode("utf-8") if isinstance(s, bytes) else s


@cache
def distro_id():
    try:
        return platform.freedesktop_os_release()["ID"]
    except (OSError, AttributeError):
        return "unknown"


def open_terminal_in_file(filename):
    """open the new terminal with correct path"""
    cmd = terminal_cmd.copy()
    if new_tab and terminal_data.new_tab_arguments:
        cmd.extend(terminal_data.new_tab_arguments)
    elif terminal_data.new_window_arguments:
        cmd.extend(terminal_data.new_window_arguments)

    if filename and terminal_data.workdir_arguments:
        cmd.extend(terminal_data.workdir_arguments)
        if terminal == "blackbox":
            # This is required
            cmd.append(filename)

    Popen(cmd, cwd=filename)


def set_terminal_args(*args):
    global new_tab
    global flatpak
    global terminal_cmd
    global terminal_data
    value = _gsettings.get_string(GSETTINGS_TERMINAL)
    newer_tab = _gsettings.get_boolean(GSETTINGS_NEW_TAB)
    flatpak = FLATPAK_PARMS[_gsettings.get_enum(GSETTINGS_FLATPAK)]
    new_terminal_data = TERMINALS.get(value)
    if not new_terminal_data:
        print('open-any-terminal: unknown terminal "{0}"'.format(value))
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
        flatpak_text = "with flatpak as {0}".format(flatpak)
    else:
        terminal_cmd = [terminal]
        if terminal == "blackbox" and distro_id() == "fedora":
            # It's called like this on fedora
            terminal_cmd[0] = "blackbox-terminal"
        flatpak = FLATPAK_PARMS[0]
        flatpak_text = ""
    print(
        'open-any-terminal: terminal is set to "{0}" {1} {2}'.format(
            terminal, new_tab_text, flatpak_text
        )
    )


if Nautilus._version == "3.0":

    class OpenAnyTerminalShortcutProvider(
        GObject.GObject, Nautilus.LocationWidgetProvider
    ):
        def __init__(self):
            source = Gio.SettingsSchemaSource.get_default()
            if source.lookup(GSETTINGS_PATH, True):
                self._gsettings = Gio.Settings.new(GSETTINGS_PATH)
                self._gsettings.connect("changed", self._bind_shortcut)
                self._create_accel_group()
            self._window = None
            self._uri = None

        def _create_accel_group(self):
            self._accel_group = Gtk.AccelGroup()
            shortcut = self._gsettings.get_string(GSETTINGS_KEYBINDINGS)
            key, mod = Gtk.accelerator_parse(shortcut)
            self._accel_group.connect(
                key, mod, Gtk.AccelFlags.VISIBLE, self._open_terminal
            )

        def _bind_shortcut(self, gsettings, key):
            if key == GSETTINGS_KEYBINDINGS:
                self._accel_group.disconnect(self._open_terminal)
                self._create_accel_group()

        def _open_terminal(self, *args):
            filename = unquote(self._uri[7:])
            open_terminal_in_file(filename)

        def get_widget(self, uri, window):
            self._uri = uri
            if self._window:
                self._window.remove_accel_group(self._accel_group)
            if self._gsettings:
                window.add_accel_group(self._accel_group)
            self._window = window
            return None


class OpenAnyTerminalExtension(GObject.GObject, Nautilus.MenuProvider):
    def _open_terminal(self, file_):
        if file_.get_uri_scheme() in REMOTE_URI_SCHEME:
            result = urlparse(file_.get_uri())

            cmd = terminal_cmd.copy()
            cmd.extend(terminal_data.command_arguments)
            cmd.extend(["ssh", "-t"])
            if result.username:
                cmd.append("{0}@{1}".format(result.username, result.hostname))
            else:
                cmd.append(result.hostname)

            if result.port:
                cmd.append("-p")
                cmd.append(str(result.port))

            if file_.is_directory():
                cmd.extend(
                    ["cd", shlex.quote(unquote(result.path)), ";", "exec", "$SHELL"]
                )

            Popen(cmd)
        else:
            filename = Gio.File.new_for_uri(file_.get_uri()).get_path()
            open_terminal_in_file(filename)

    def _menu_activate_cb(self, menu, file_):
        self._open_terminal(file_)

    def _menu_background_activate_cb(self, menu, file_):
        self._open_terminal(file_)

    def get_file_items(self, *args):
        # `args` will be `[files: List[Nautilus.FileInfo]]` in Nautilus 4.0 API,
        # and `[window: Gtk.Widget, files: List[Nautilus.FileInfo]]` in Nautilus 3.0 API.

        files = args[-1]

        if len(files) != 1:
            return
        items = []
        file_ = files[0]

        if file_.is_directory():
            if file_.get_uri_scheme() in REMOTE_URI_SCHEME:
                uri = _checkdecode(file_.get_uri())
                item = Nautilus.MenuItem(
                    name="NautilusPython::open_remote_item",
                    label=_("Open Remote {}").format(terminal_data.name),
                    tip=_("Open Remote {} In {}").format(terminal_data.name, uri),
                )
                item.connect("activate", self._menu_activate_cb, file_)
                items.append(item)

            filename = _checkdecode(file_.get_name())
            item = Nautilus.MenuItem(
                name="NautilusPython::open_file_item",
                label=_("Open In {}").format(terminal_data.name),
                tip=_("Open {} In {}").format(terminal_data.name, filename),
            )
            item.connect("activate", self._menu_activate_cb, file_)
            items.append(item)

        return items

    def get_background_items(self, *args):
        # `args` will be `[folder: Nautilus.FileInfo]` in Nautilus 4.0 API,
        # and `[window: Gtk.Widget, file: Nautilus.FileInfo]` in Nautilus 3.0 API.

        file_ = args[-1]

        items = []
        if file_.get_uri_scheme() in REMOTE_URI_SCHEME:
            item = Nautilus.MenuItem(
                name="NautilusPython::open_bg_remote_item",
                label=_("Open Remote {} Here").format(terminal_data.name),
                tip=_("Open Remote {} In This Directory").format(terminal_data.name),
            )
            item.connect("activate", self._menu_activate_cb, file_)
            items.append(item)

        item = Nautilus.MenuItem(
            name="NautilusPython::open_bg_file_item",
            label=_("Open {} Here").format(terminal_data.name),
            tip=_("Open {} In This Directory").format(terminal_data.name),
        )
        item.connect("activate", self._menu_background_activate_cb, file_)
        items.append(item)
        return items


source = Gio.SettingsSchemaSource.get_default()
if source is not None and source.lookup(GSETTINGS_PATH, True):
    _gsettings = Gio.Settings.new(GSETTINGS_PATH)
    _gsettings.connect("changed", set_terminal_args)
    set_terminal_args()
