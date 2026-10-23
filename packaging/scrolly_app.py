"""Entry point of the Scrolly executable: the server behind its small window.

A windowed app has no console, so what Scrolly would print goes to scrolly.log in the data folder.
Arguments pass through (`--no-browser`, `--port`), which the release workflow uses for its check.
"""

import sys

from scrolly.cli import main
from scrolly.config import data_dir

if sys.stdout is None or sys.stderr is None:
    log = open(data_dir() / "scrolly.log", "a", encoding="utf-8")  # noqa: SIM115 - lives as long as the app
    sys.stdout = sys.stderr = log

# Finder may add a process-serial-number argument on older macOS; it is not ours.
main(["--window", *(arg for arg in sys.argv[1:] if not arg.startswith("-psn"))])
