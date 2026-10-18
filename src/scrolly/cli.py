import argparse
import threading
import webbrowser

import uvicorn

from scrolly import instance
from scrolly.bootstrap import build_app


def main() -> None:
    parser = argparse.ArgumentParser(prog="scrolly", description="Run Scrolly locally.")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    existing = instance.running_port()
    if existing is not None:
        if not args.no_browser:
            webbrowser.open(f"http://127.0.0.1:{existing}")
        return

    port = instance.pick_port(args.port)
    app = build_app()
    instance.remember(port)
    if not args.no_browser:
        threading.Timer(1.0, webbrowser.open, [f"http://127.0.0.1:{port}"]).start()
    try:
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
    finally:
        instance.forget()
