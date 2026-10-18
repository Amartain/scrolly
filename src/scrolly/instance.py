import json
import socket
import urllib.error
import urllib.request
from pathlib import Path

from scrolly.config import DEFAULT_PORT, data_dir


def _lock_file() -> Path:
    return data_dir() / "server.json"


def running_port() -> int | None:
    """The port of an already running Scrolly, if one answers."""
    try:
        port = int(json.loads(_lock_file().read_text())["port"])
        url = f"http://127.0.0.1:{port}/api/health"
        with urllib.request.urlopen(url, timeout=1) as reply:
            return port if json.load(reply).get("app") == "scrolly" else None
    except (OSError, ValueError, KeyError, urllib.error.URLError):
        return None


def _is_free(port: int) -> bool:
    with socket.socket() as probe:
        return probe.connect_ex(("127.0.0.1", port)) != 0


def pick_port(requested: int | None) -> int:
    """The requested port as is; otherwise the default, or any free one."""
    if requested is not None:
        return requested
    if _is_free(DEFAULT_PORT):
        return DEFAULT_PORT
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def remember(port: int) -> None:
    _lock_file().write_text(json.dumps({"port": port}))


def forget() -> None:
    _lock_file().unlink(missing_ok=True)
