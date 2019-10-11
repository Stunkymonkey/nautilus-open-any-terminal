#!/usr/bin/env python
# encoding: UTF-8

import os
from setuptools import setup, find_packages
from setuptools.command.install import install as _install

from nautilus_open_any_terminal import VERSION


class install(_install):
    def run(self):
        _install.run(self)

        # Do what distutils install_data used to do... *sigh*
        # Despite what the setuptools docs say, the omission of this
        # in setuptools is a bug, not a feature.
        print("== Installing Nautilus Python extension...")
        src_file = "nautilus_open_any_terminal/open_any_terminal_extension.py"
        dst_dir = os.path.join(self.install_data, "share/nautilus-python/extensions")
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
        print("== Done! Run 'glib-compile-schemas /usr/share/glib-2.0/schemas/' for a global installation to compile the schema.")


long_description = ""
long_description_content_type = 'text/x-rst'
if os.path.isfile("README.rst"):
    long_description = open("README.rst", "r").read()
    long_description_content_type = 'text/x-rst'
elif os.path.isfile("README.md"):
    long_description = open("README.md", "r").read()
    long_description_content_type = 'text/markdown'


setup(
    name="nautilus_open_any_terminal",
    version=VERSION,
    description="new variable terminal entry in contextmenu",
    url="https://github.com/Stunkymonkey/nautilus-open-any-terminal",
    license="GPL-3.0",

    long_description=long_description,
    long_description_content_type=long_description_content_type,

    author="Felix Bühler",

    keywords="nautilus extension terminal gnome",
    platforms=["Linux", "BSD"],

    packages=find_packages(),
    include_package_data=True,

    cmdclass={"install": install}
)
