import subprocess
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from setuptools.command.sdist import sdist

FILE_MANAGERS = ["nautilus", "caja"]


def build_mo():
    for po_path in Path("nautilus_open_any_terminal/locale").glob("*.po"):
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
        for fm in FILE_MANAGERS:
            dst_dir = Path(self.install_data) / f"share/{fm}-python/extensions"
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst_file = dst_dir / src_file.name
            self.copy_file(src_file, dst_file)
        print("== Done!")

        # Install language files
        print("== Installing language files")
        for src_file in Path("nautilus_open_any_terminal/locale").glob("*.mo"):
            dst_dir = Path(self.install_data) / "share/locale" / src_file.stem / "LC_MESSAGES"
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst_file = dst_dir / "nautilus-open-any-terminal.mo"
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
    package_data={"nautilus-open-any-terminal": ["locale/*.mo"]},
    include_package_data=True,
    cmdclass={
        "install": InstallCommand,
        "sdist": SdistCommand,
        "build_py": BuildCommand,
    },
)
