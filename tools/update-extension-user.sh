#!/usr/bin/env sh

# Make the extension available to the current user.

SRC=nautilus_open_any_terminal/open_any_terminal_extension.py
TARGDIR=~/.local/share/nautilus-python/extensions

SCHEMASDIR=~/.local/share/glib-2.0/schemas/
SCHEMASSRC=nautilus_open_any_terminal/schemas
SCHEMAFILE=com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml

LANGUAGEDIR=~/.local/locale
LANGUAGESRC=nautilus_open_any_terminal/locale
LANGUAGEFILE=nautilus-open-any-terminal.mo

bn=$(basename "$SRC")

case "$1" in
    install)
        # copy nautilus files
        mkdir -v -p "$TARGDIR"
        chmod 0755 "$TARGDIR"
        cp -v "$SRC" "$TARGDIR/$bn"
        chmod -c 0644 "$TARGDIR/$bn"
        # copy language files
        cd "$LANGUAGESRC" || exit
        find . -name '*.mo' -exec cp -v --parents '{}' "$LANGUAGEDIR" \;
        cd ../..
        find . -name '*.mo' -exec chmod -c 0644 '{}' \;
        # copy schema file
        cp -v "$SCHEMASSRC/$SCHEMAFILE" "$SCHEMASDIR"
        glib-compile-schemas $SCHEMASDIR
        ;;
    uninstall)
        rm -vf "$TARGDIR/$bn"
        find $LANGUAGEDIR -type f -name "$LANGUAGEFILE" -exec rm -vf '{}' \;
        rm -vf $SCHEMASDIR/$SCHEMAFILE
        glib-compile-schemas $SCHEMASDIR
        ;;
    *)
        echo >&2 "usage: $0 {install|uninstall}"
        ;;
esac
