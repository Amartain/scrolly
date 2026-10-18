"""Build the frontend into src/scrolly/static, then the wheel into dist/."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NPM = shutil.which("npm") or "npm"


def main() -> int:
    steps = [
        ([NPM, "ci"], ROOT / "frontend"),
        ([NPM, "run", "build"], ROOT / "frontend"),
        ([sys.executable, "-m", "build", "--wheel"], ROOT),
    ]
    for command, folder in steps:
        if subprocess.run(command, cwd=folder, check=False).returncode != 0:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
