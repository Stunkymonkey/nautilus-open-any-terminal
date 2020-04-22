#!/usr/bin/env sh

# Make the extension available to the current user.

SRC=nautilus_open_any_terminal/open_any_terminal_extension.py
TARGDIR=~/.local/share/nautilus-python/extensions

SCHEMASDIR=~/.local/share/glib-2.0/schemas/
SCHEMAFILE=com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml


bn=`basename "$SRC"`

case "$1" in
    install)
        mkdir -v -p "$TARGDIR"
        cp -v "$SRC" "$TARGDIR/$bn"
        chmod -c 0644 "$TARGDIR/$bn"
        glib-compile-schemas $SCHEMASDIR
        ;;
    uninstall)
        rm -vf "$TARGDIR/$bn"
        rm -vf $SCHEMASDIR/$SCHEMAFILE
        glib-compile-schemas $SCHEMASDIR
        ;;
    *)
        echo >&2 "usage: $0 {install|uninstall}"
        ;;
esac
