#!/usr/bin/env sh

# Make the extension available to the current user.

SRC=nautilus_open_any_terminal/open_any_terminal_extension.py
TARGDIR=~/.local/share/nautilus-python/extensions

bn=`basename "$SRC"`

case "$1" in
    install)
        mkdir -v -p "$TARGDIR"
        cp -v "$SRC" "$TARGDIR/$bn"
        ;;
    uninstall)
        rm -vf "$TARGDIR/$bn"
        ;;
    *)
        echo >&2 "usage: $0 {install|uninstall}"
        ;;
esac
