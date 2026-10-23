"""Build the Scrolly executable for this computer, zipped for sharing: `uv run poe exe`.

Windows: dist/Scrolly-<version>-windows.zip (a Scrolly folder with Scrolly.exe).
macOS: dist/Scrolly-<version>-macos-<arch>.zip (Scrolly.app). PyInstaller cannot build for another
system, so each zip is built on its own system (the release workflow does both).
"""

import platform
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
NPM = shutil.which("npm") or "npm"


def version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as file:
        return str(tomllib.load(file)["project"]["version"])


def zip_name() -> str:
    if sys.platform == "darwin":
        return f"Scrolly-{version()}-macos-{platform.machine()}.zip"
    if sys.platform == "win32":
        return f"Scrolly-{version()}-windows.zip"
    return f"Scrolly-{version()}-linux-{platform.machine()}.zip"


def run(command: list[str], folder: Path) -> bool:
    return subprocess.run(command, cwd=folder, check=False).returncode == 0


def main() -> int:
    built = DIST / "exe"
    work = ROOT / "build" / "pyinstaller"
    frontend = ROOT / "frontend"
    # A fresh checkout installs; an existing one is kept (a running dev server locks files in it).
    install = [] if (frontend / "node_modules").exists() else [([NPM, "ci"], frontend)]
    steps = [
        *install,
        ([NPM, "run", "build"], frontend),
        (
            [
                *(sys.executable, "-m", "PyInstaller", "packaging/scrolly.spec", "--noconfirm"),
                *("--distpath", str(built), "--workpath", str(work)),
            ],
            ROOT,
        ),
    ]
    for command, folder in steps:
        if not run(command, folder):
            return 1

    archive = DIST / zip_name()
    archive.unlink(missing_ok=True)
    if sys.platform == "darwin":
        # ditto keeps the app's symlinks and permissions, which a plain zip would break.
        command = ["ditto", "-c", "-k", "--keepParent", "Scrolly.app", str(archive)]
        if not run(command, built):
            return 1
    else:
        shutil.make_archive(str(archive.with_suffix("")), "zip", built, "Scrolly")
    print(f"Built {archive.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
