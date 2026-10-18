"""Frontend half of `poe check`: types, formatting, build, then end-to-end tests."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
NPM = shutil.which("npm") or "npm"
NPX = shutil.which("npx") or "npx"
STEPS = [
    [NPM, "run", "check"],
    [NPM, "run", "format:check"],
    [NPM, "run", "build"],
    [NPX, "playwright", "test"],
]


def main() -> int:
    env = {**os.environ, "SCROLLY_PYTHON": sys.executable}
    for step in STEPS:
        print(f"> {' '.join(step[1:])}", flush=True)
        if subprocess.run(step, cwd=FRONTEND, env=env, check=False).returncode != 0:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
