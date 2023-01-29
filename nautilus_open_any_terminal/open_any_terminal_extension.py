# -*- coding: utf-8 -*-
# based on: https://github.com/gnunn1/tilix/blob/master/data/nautilus/open-tilix.py

from gettext import gettext, translation
from os import environ
from subprocess import call

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

TERM_WORKDIR_PARAMS = {
    "alacritty": "--working-directory ",
    "blackbox": "--working-directory ",
    "cool-retro-term": "--workdir ",
    "deepin-terminal": "--work-directory ",
    "foot": "--working-directory=",
    "footclient": "--working-directory=",
    "gnome-terminal": "--working-directory=",
    "guake": "guake --show --new-tab=",
    "hyper": "",
    "kermit": "-w ",
    "kgx": "--working-directory=",
    "kitty": "--directory ",
    "konsole": "--workdir ",
    "mate-terminal": "--working-directory=",
    "mlterm": "--working-directory=",
    "qterminal": "--workdir ",
    "sakura": "-d ",
    "st": "-d ",
    "terminator": "--working-directory=",
    "terminology": "--current-directory ",
    "termite": "-d ",
    "tilix": "-w ",
    "urxvt": "-cd ",
    "urxvtc": "-cd ",
    "wezterm": "start --cwd ",
    "xfce4-terminal": "--working-directory=",
    "tabby": "open ",
}

NEW_TAB_PARAMS = {
    "alacritty": None,
    "blackbox": None,
    "cool-retro-term": None,
    "deepin-terminal": None,
    "foot": None,
    "footclient": None,
    "gnome-terminal": "--tab",
    "guake": None,
    "hyper": None,
    "kermit": None,
    "kgx": "--tab",
    "kitty": None,
    "konsole": "--new-tab",
    "mate-terminal": "--tab",
    "mlterm": None,
    "qterminal": None,
    "sakura": None,
    "st": None,
    "terminator": "--new-tab",
    "terminology": None,
    "termite": None,
    "tilix": None,
    "urxvt": None,
    "urxvtc": None,
    "wezterm": None,
    "xfce4-terminal": "--tab",
    "tabby": None,
}

TERM_CMD_PARAMS = {
    "alacritty": "-e",
    "blackbox": "-c",
    "cool-retro-term": "-e",
    "deepin-terminal": "-e",
    "foot": "-e",
    "footclient": "-e",
    "gnome-terminal": "-e",
    "guake": "-e",
    "hyper": "-e",
    "kermit": "-e",
    "kgx": "-e",
    "kitty": "-e",
    "konsole": "-e",
    "mate-terminal": "-e",
    "mlterm": "-e",
    "qterminal": "-e",
    "sakura": "-e",
    "st": "-e",
    "terminator": "-e",
    "terminology": "-e",
    "termite": "-e",
    "tilix": "-e",
    "urxvt": "-e",
    "urxvtc": "-e",
    "wezterm": "-e",
    "xfce4-terminal": "-e",
    "tabby": "-e",
}

TERM_NAME = {
    "alacritty": "Alacritty",
    "blackbox": "Black Box",
    "cool-retro-term": "cool-retro-term",
    "deepin-terminal": "Deepin Terminal",
    "foot": "Foot",
    "footclient": "FootClient",
    "gnome-terminal": "Terminal",
    "guake": "Guake",
    "hyper": "Hyper",
    "kermit": "Kermit",
    "kgx": "Console",
    "kitty": "kitty",
    "konsole": "Konsole",
    "mate-terminal": "Mate Terminal",
    "mlterm": "Mlterm",
    "qterminal": "QTerminal",
    "sakura": "Sakura",
    "st": "Simple Terminal",
    "terminator": "Terminator",
    "terminology": "Terminology",
    "termite": "Termite",
    "tilix": "Tilix",
    "urxvt": "rxvt-unicode",
    "urxvtc": "urxvtc",
    "wezterm": "Wez's Terminal Emulator",
    "xfce4-terminal": "Xfce Terminal",
    "tabby": "Tabby",
}

FLATPAK_PARMS = ["off", "system", "user"]

FLATPAK_NAMES = {
    "blackbox": "com.raggesilver.BlackBox",
    "tilix": "com.gexperts.Tilix",
}

global terminal
terminal = "gnome-terminal"
terminal_cmd = None
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


def open_terminal_in_file(filename):
    """open the new terminal with correct path"""
    if filename:
        # escape filename quotations
        filename = filename.replace('"', '\\"')
        if new_tab:
            call(
                '{0} {1} {2}"{3}" &'.format(
                    terminal_cmd,
                    NEW_TAB_PARAMS[terminal],
                    TERM_WORKDIR_PARAMS[terminal],
                    filename,
                ),
                shell=True,
            )
        else:
            call(
                '{0} {1}"{2}" &'.format(
                    terminal_cmd, TERM_WORKDIR_PARAMS[terminal], filename
                ),
                shell=True,
            )
    else:
        call("{0} &".format(terminal_cmd), shell=True)


def set_terminal_args(*args):
    global new_tab
    global flatpak
    global terminal_cmd
    value = _gsettings.get_string(GSETTINGS_TERMINAL)
    newer_tab = _gsettings.get_boolean(GSETTINGS_NEW_TAB)
    flatpak = FLATPAK_PARMS[_gsettings.get_enum(GSETTINGS_FLATPAK)]
    if value in TERM_WORKDIR_PARAMS:
        global terminal
        terminal = value
        if newer_tab and NEW_TAB_PARAMS[terminal] is not None:
            new_tab = newer_tab
            new_tab_text = "opening in a new tab"
        else:
            new_tab_text = "opening a new window"
        if newer_tab and NEW_TAB_PARAMS[terminal] is None:
            new_tab_text += " (terminal does not support tabs)"
        if flatpak != FLATPAK_PARMS[0] and value in FLATPAK_NAMES:
            terminal_cmd = "flatpak run --{0} {1}".format(
                flatpak, FLATPAK_NAMES[terminal]
            )
            flatpak_text = "with flatpak as {0}".format(flatpak)
        else:
            terminal_cmd = terminal
            flatpak = FLATPAK_PARMS[0]
            flatpak_text = ""
        print(
            'open-any-terminal: terminal is set to "{0}" {1} {2}'.format(
                terminal, new_tab_text, flatpak_text
            )
        )
    else:
        print('open-any-terminal: unknown terminal "{0}"'.format(value))


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
            if result.username:
                value = "ssh -t {0}@{1}".format(result.username, result.hostname)
            else:
                value = "ssh -t {0}".format(result.hostname)
            if result.port:
                value = "{0} -p {1}".format(value, result.port)
            if file_.is_directory():
                value = '{0} cd "{1}" \\; $SHELL'.format(value, result.path)

            call(
                '{0} {1} "{2}" &'.format(
                    terminal_cmd, TERM_CMD_PARAMS[terminal], value
                ),
                shell=True,
            )
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
                    label=_("Open Remote {}").format(TERM_NAME[terminal]),
                    tip=_("Open Remote {} In {}").format(TERM_NAME[terminal], uri),
                )
                item.connect("activate", self._menu_activate_cb, file_)
                items.append(item)

            filename = _checkdecode(file_.get_name())
            item = Nautilus.MenuItem(
                name="NautilusPython::open_file_item",
                label=_("Open In {}").format(TERM_NAME[terminal]),
                tip=_("Open {} In {}").format(TERM_NAME[terminal], filename),
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
                label=_("Open Remote {} Here").format(TERM_NAME[terminal]),
                tip=_("Open Remote {} In This Directory").format(TERM_NAME[terminal]),
            )
            item.connect("activate", self._menu_activate_cb, file_)
            items.append(item)

        item = Nautilus.MenuItem(
            name="NautilusPython::open_bg_file_item",
            label=_("Open {} Here").format(TERM_NAME[terminal]),
            tip=_("Open {} In This Directory").format(TERM_NAME[terminal]),
        )
        item.connect("activate", self._menu_background_activate_cb, file_)
        items.append(item)
        return items


source = Gio.SettingsSchemaSource.get_default()
if source is not None and source.lookup(GSETTINGS_PATH, True):
    _gsettings = Gio.Settings.new(GSETTINGS_PATH)
    _gsettings.connect("changed", set_terminal_args)
    set_terminal_args()
