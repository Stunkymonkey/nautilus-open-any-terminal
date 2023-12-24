#!/bin/sh

# Make the extension available to the current user.

SRC=src/nautilus_open_any_terminal.py
TARGDIR=~/.local/share/nautilus-python/extensions

SCHEMASDIR=~/.local/share/glib-2.0/schemas
SCHEMASSRC=src/schemas
SCHEMAFILE=com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml

LANGUAGEDIR=~/.local/share/locale
LANGUAGESRC=src/locale
LANGUAGEFILE=nautilus-open-any-terminal.mo

case "$1" in
    install)
        # copy nautilus files
        install -Dvm644 "${SRC}" -t "${TARGDIR}"
        # copy language files
        mkdir -vp "${LANGUAGEDIR}"
        oldpwd="${PWD}"
        cd "$LANGUAGESRC" || exit
        find . -name '*.po' | while read -r po_file;do
            msgfmt -o "${po_file%.po}.mo" "${po_file}"
        done
        find . -name '*.mo' -exec cp -v --parents '{}' "${LANGUAGEDIR}" \;
        cd "${oldpwd}" || exit
        find . -name '*.mo' -exec chmod -c 0644 '{}' \;
        # copy schema file
        install -Dv "${SCHEMASSRC}/${SCHEMAFILE}" -t "${SCHEMASDIR}"
        glib-compile-schemas "${SCHEMASDIR}"
        ;;
    uninstall)
        rm -vf "${TARGDIR}/$(basename "${SRC}")"
        find "${LANGUAGEDIR}" -type f -name "${LANGUAGEFILE}" -exec rm -vf '{}' \;
        rm -vf "${SCHEMASDIR}/${SCHEMAFILE}"
        glib-compile-schemas "${SCHEMASDIR}"
        ;;
    *)
        echo >&2 "usage: $0 {install|uninstall}"
        ;;
esac
