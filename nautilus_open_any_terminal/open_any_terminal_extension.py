# -*- coding: UTF-8 -*-
# based on: https://github.com/gnunn1/tilix/blob/master/data/nautilus/open-tilix.py

from gettext import gettext, textdomain
from subprocess import call
try:
    from urllib import unquote
    from urlparse import urlparse
except ImportError:
    from urllib.parse import unquote, urlparse

from gi import require_version
require_version('Gtk', '3.0')
require_version('Nautilus', '3.0')
from gi.repository import Gio, GObject, Gtk, Nautilus

VERSION = "0.2.1"

TERM_PARAMS = {"alacritty": "--working-directory ",
               "cool-retro-term": "--workdir ",
               "gnome-terminal": "",
               "kitty": "--directory ",
               "konsole": "--workdir ",
               "mlterm": "--working-directory=",
               "qterminal": "--workdir ",
               "terminator": "--working-directory=",
               "terminology": "--current-directory ",
               "tilix": "-x ",
               "xfce4-terminal": "--working-directory="}

NEW_TAB_PARAMS = {"alacritty": None,
                  "cool-retro-term": None,
                  "gnome-terminal": "--tab",
                  "kitty": None,
                  "konsole": "--new-tab",
                  "mlterm": None,
                  "qterminal": None,
                  "terminator": "--new-tab",
                  "terminology": None,
                  "tilix": None,
                  "xfce4-terminal": "--tab"}

global terminal
terminal = "gnome-terminal"
new_tab = False
GSETTINGS_PATH = "com.github.stunkymonkey.nautilus-open-any-terminal"
GSETTINGS_KEYBINDINGS = "keybindings"
GSETTINGS_TERMINAL = "terminal"
GSETTINGS_NEW_TAB = "new-tab"
REMOTE_URI_SCHEME = ["ftp", "sftp"]
textdomain("nautilus-open-any-terminal")
_ = gettext


def _checkdecode(s):
    """Decode string assuming utf encoding if it's bytes, else return unmodified"""
    return s.decode('utf-8') if isinstance(s, bytes) else s


def open_terminal_in_file(filename):
    if filename:
        # print('{0} {1} {2} "{3}" &'.format(terminal, NEW_TAB_PARAMS[terminal], TERM_PARAMS[terminal], filename))
        if new_tab:
            call('{0} {1} {2}"{3}" &'.format(terminal, NEW_TAB_PARAMS[
                 terminal], TERM_PARAMS[terminal], filename), shell=True)
        else:
            call('{0} {1}"{2}" &'.format(terminal, TERM_PARAMS[terminal], filename), shell=True)
    else:
        call("{0} &".format(terminal), shell=True)


def set_terminal_args(*args):
    global new_tab
    value = _gsettings.get_string(GSETTINGS_TERMINAL)
    newer_tab = _gsettings.get_boolean(GSETTINGS_NEW_TAB)
    if value in TERM_PARAMS:
        global terminal
        terminal = value
        if newer_tab and NEW_TAB_PARAMS[terminal] is not None:
            new_tab = newer_tab
            new_tab_text = "opening in a new tab"
        else:
            new_tab_text = "opening a new window"
        if newer_tab and NEW_TAB_PARAMS[terminal] is None:
            new_tab_text += " (terminal does not support tabs)"
        print('open-any-terminal: terminal is set to "{0}" {1}'.format(terminal, new_tab_text))
    else:
        print('open-any-terminal: unknown terminal "{0}"'.format(value))


class OpenAnyTerminalShortcutProvider(GObject.GObject, Nautilus.LocationWidgetProvider):

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
        self._accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE,
                                  self._open_terminal)

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
                value = "ssh -t {0}@{1}".format(result.username,
                                                result.hostname)
            else:
                value = "ssh -t {0}".format(result.hostname)
            if result.port:
                value = "{0} -p {1}".format(value, result.port)
            if file_.is_directory():
                value = '{0} cd "{1}" ; $SHELL'.format(value, result.path)

            call('{0} -e "{1}" &'.format(terminal, value), shell=True)
        else:
            filename = Gio.File.new_for_uri(file_.get_uri()).get_path()
            open_terminal_in_file(filename)

    def _menu_activate_cb(self, menu, file_):
        self._open_terminal(file_)

    def _menu_background_activate_cb(self, menu, file_):
        self._open_terminal(file_)

    def get_file_items(self, window, files):
        if len(files) != 1:
            return
        items = []
        file_ = files[0]

        if file_.is_directory():

            if file_.get_uri_scheme() in REMOTE_URI_SCHEME:
                uri = _checkdecode(file_.get_uri())
                item = Nautilus.MenuItem(name="NautilusPython::open_remote_item",
                                         label=_(u'Open Remote {}').format(terminal.title()),
                                         tip=_(u'Open Remote {} In {}').format(terminal.title(), uri))
                item.connect("activate", self._menu_activate_cb, file_)
                items.append(item)

            filename = _checkdecode(file_.get_name())
            item = Nautilus.MenuItem(name="NautilusPython::open_file_item",
                                     label=_(u'Open In {}').format(terminal.title()),
                                     tip=_(u'Open {} In {}').format(terminal.title(), filename))
            item.connect("activate", self._menu_activate_cb, file_)
            items.append(item)

        return items

    def get_background_items(self, window, file_):
        items = []
        if file_.get_uri_scheme() in REMOTE_URI_SCHEME:
            item = Nautilus.MenuItem(name="NautilusPython::open_bg_remote_item",
                                     label=_(u'Open Remote {} Here').format(terminal.title()),
                                     tip=_(u'Open Remote {} In This Directory').format(terminal.title()))
            item.connect("activate", self._menu_activate_cb, file_)
            items.append(item)

        item = Nautilus.MenuItem(name="NautilusPython::open_bg_file_item",
                                 label=_(u'Open {} Here').format(terminal.title()),
                                 tip=_(u'Open {} In This Directory').format(terminal.title()))
        item.connect("activate", self._menu_background_activate_cb, file_)
        items.append(item)
        return items


source = Gio.SettingsSchemaSource.get_default()
if source.lookup(GSETTINGS_PATH, True):
    _gsettings = Gio.Settings.new(GSETTINGS_PATH)
    _gsettings.connect("changed", set_terminal_args)
    value = _gsettings.get_string(GSETTINGS_TERMINAL)
    if value in TERM_PARAMS:
        terminal = value
    if _gsettings.get_boolean(GSETTINGS_NEW_TAB):
        new_tab = bool(NEW_TAB_PARAMS[value] is not None)
