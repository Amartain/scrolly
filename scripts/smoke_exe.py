"""Start the built executable once and check it serves: `uv run python scripts/smoke_exe.py`.

It runs on an empty data folder, so the migrations, the content files and the frontend are all
read from inside the bundle. The release workflow runs it after `poe exe`.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILT = ROOT / "dist" / "exe"
PORT = 4799
URL = f"http://127.0.0.1:{PORT}"


def executable() -> Path:
    if sys.platform == "darwin":
        return BUILT / "Scrolly.app" / "Contents" / "MacOS" / "Scrolly"
    return BUILT / "Scrolly" / ("Scrolly.exe" if sys.platform == "win32" else "Scrolly")


def get(path: str) -> bytes:
    with urllib.request.urlopen(URL + path, timeout=2) as reply:
        return bytes(reply.read())


def wait_until_up(seconds: int = 60) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            return bool(json.loads(get("/api/health")).get("app") == "scrolly")
        except OSError:
            time.sleep(0.5)
    return False


def main() -> int:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as home:
        env = {**os.environ, "SCROLLY_HOME": home}
        command = [str(executable()), "--no-browser", "--port", str(PORT)]
        app = subprocess.Popen(command, env=env)
        try:
            if not wait_until_up():
                print("The executable did not answer.")
                return 1
            checks = {
                "page": b'id="app"' in get("/"),
                "view": "planning" in json.loads(get("/api/view")),
                "database": (Path(home) / "scrolly.db").exists(),
            }
        finally:
            app.terminate()
            app.wait(timeout=15)
        for name, passed in checks.items():
            print(f"{name}: {'ok' if passed else 'FAILED'}")
        return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
