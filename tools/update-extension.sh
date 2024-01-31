#!/bin/sh

# Make the extension available to the current user or system.
#
# The Python integration for Nautilus doesn't seem to respect /usr/local
# prefixes despite its docs saying it should. For now, global installs
# need the extension module to go in the /usr location only.
#
# This script also compiles GSettings schemas

if [ "$(id -u)" -eq 0 ]; then
  PREFIX="/usr"
else
  PREFIX="${HOME}/.local"
fi

SRC=nautilus_open_any_terminal/nautilus_open_any_terminal.py
TARGDIR="${PREFIX}/share/nautilus-python/extensions"

SCHEMASDIR="${PREFIX}/share/glib-2.0/schemas"
SCHEMASSRC=nautilus_open_any_terminal/schemas
SCHEMAFILE=com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml

LANGUAGEDIR="${PREFIX}/share/locale"
LANGUAGESRC=nautilus_open_any_terminal/locale
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
