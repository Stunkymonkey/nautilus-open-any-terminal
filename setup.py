import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from setuptools.command.sdist import sdist

TRANSLATIONS_STEM = "locale/*/LC_MESSAGES/nautilus-open-any-terminal"
PO_FILES = TRANSLATIONS_STEM + ".po"
MO_FILES = TRANSLATIONS_STEM + ".mo"


def build_mo():
    for po_path in Path("nautilus_open_any_terminal").glob(PO_FILES):
        mo = po_path.with_suffix(".mo")
        subprocess.run(["msgfmt", "-o", mo, po_path], check=True)


class SdistCommand(sdist):
    def run(self):
        build_mo()
        super().run()


class BuildCommand(build_py):
    def run(self):
        build_mo()
        super().run()


class InstallCommand(install):
    def run(self):
        super().run()

        # Install Nautilus Python extension
        print("== Installing Nautilus Python extension")
        src_file = Path("nautilus_open_any_terminal/nautilus_open_any_terminal.py")
        dst_dir = Path(self.install_data) / "share/nautilus-python/extensions"
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_file = dst_dir / src_file.name
        self.copy_file(src_file, dst_file)
        print("== Done!")

        # Install language files
        print("== Installing language files")
        for src_file in Path("nautilus_open_any_terminal").glob(MO_FILES):
            original_folder = src_file.relative_to("nautilus_open_any_terminal").parent
            dst_dir = Path(self.install_data) / "share" / original_folder
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst_file = dst_dir / src_file.name
            self.copy_file(src_file, dst_file)
        print("== Done!")

        # Install GSettings Schema
        print("== Installing GSettings Schema")
        src_file = Path(
            "./nautilus_open_any_terminal/schemas/com.github.stunkymonkey.nautilus-open-any-terminal.gschema.xml"
        )
        dst_dir = Path(self.install_data) / "share/glib-2.0/schemas"
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_file = dst_dir / src_file.name
        self.copy_file(src_file, dst_file)
        print(f"== Done! Run 'glib-compile-schemas {dst_dir}' to compile the schema.")


setup(
    package_data={"nautilus-open-any-terminal": [MO_FILES]},
    include_package_data=True,
    cmdclass={
        "install": InstallCommand,
        "sdist": SdistCommand,
        "build_py": BuildCommand,
    },
)
