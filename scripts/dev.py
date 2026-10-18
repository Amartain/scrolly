"""Run the API (auto-reload, port 4748) and the Vite dev server together."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NPM = shutil.which("npm") or "npm"


def main() -> int:
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "scrolly.api.dev:app", "--reload", "--port", "4748"],
        cwd=ROOT,
    )
    web = subprocess.Popen([NPM, "run", "dev", "--", "--open"], cwd=ROOT / "frontend")
    try:
        return web.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        for process in (web, api):
            process.terminate()


if __name__ == "__main__":
    sys.exit(main())
