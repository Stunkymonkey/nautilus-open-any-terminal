#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import pathlib
import subprocess

from nautilus_open_any_terminal import VERSION
from setuptools import find_packages, setup
from setuptools.command.install import install as _install

PO_FILES = "locale/*/LC_MESSAGES/nautilus-open-any-terminal.po"


def create_mo_files():
    mo_files = []
    prefix = "nautilus_open_any_terminal"

    for po_path in glob.glob(str(pathlib.Path(prefix) / PO_FILES)):
        mo = pathlib.Path(po_path.replace(".po", ".mo"))

        subprocess.run(["msgfmt", "-o", str(mo), po_path], check=True)
        mo_files.append(str(mo.relative_to(prefix)))

    return mo_files


class install(_install):
    def run(self):
        _install.run(self)

        # Do what distutils install_data used to do... *sigh*
        # Despite what the setuptools docs say, the omission of this
        # in setuptools is a bug, not a feature.
        print("== Installing Nautilus Python extension")
        src_file = "nautilus_open_any_terminal/open_any_terminal_extension.py"
        dst_dir = os.path.join(self.install_data, "share/nautilus-python/extensions")
        self.mkpath(dst_dir)
        dst_file = os.path.join(dst_dir, os.path.basename(src_file))
        self.copy_file(src_file, dst_file)
        print("== Done!")

        print("== Installing language files")
        for po_path in glob.glob(
            str(pathlib.Path("nautilus_open_any_terminal") / PO_FILES)
        ):
            src_file = pathlib.Path(po_path.replace(".po", ".mo"))
            original_folder = os.path.dirname(src_file).replace(
                "nautilus_open_any_terminal/", ""
            )
            dst_dir = os.path.join(self.install_data, "share", original_folder)
            self.mkpath(dst_dir)
            dst_file = os.path.join(dst_dir, os.path.basename(src_file))
            self.copy_file(src_file, dst_file)
        print("== Done!")

        print("== Installing GSettings Schema")
        src_file = "./nautilus_open_any_terminal/schemas/com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml"
        dst_dir = os.path.join(self.install_data, "share/glib-2.0/schemas")
        self.mkpath(dst_dir)
        dst_file = os.path.join(dst_dir, os.path.basename(src_file))
        self.copy_file(src_file, dst_file)
        print(
            "== Done! Run 'glib-compile-schemas "
            + dst_dir
            + "/' to compile the schema."
        )


long_description = ""
long_description_content_type = "text/x-rst"
if os.path.isfile("README.rst"):
    long_description = open("README.rst", "r").read()
    long_description_content_type = "text/x-rst"
elif os.path.isfile("README.md"):
    long_description = open("README.md", "r").read()
    long_description_content_type = "text/markdown"


setup(
    name="nautilus_open_any_terminal",
    version=VERSION,
    description="new variable terminal entry in contextmenu",
    url="https://github.com/Stunkymonkey/nautilus-open-any-terminal",
    license="GPL-3.0",
    long_description=long_description,
    long_description_content_type=long_description_content_type,
    author="Felix Bühler",
    author_email="account@buehler.rocks",
    keywords="nautilus extension terminal gnome",
    platforms=["Linux", "BSD"],
    packages=find_packages(),
    package_data={"nautilus-open-any-terminal": create_mo_files()},
    include_package_data=True,
    cmdclass={"install": install},
)
