import argparse
import threading
import webbrowser

import uvicorn

from scrolly import instance, window
from scrolly.bootstrap import build_app


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="scrolly", description="Run Scrolly locally.")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument(
        "--window", action="store_true", help="show a small window to open Scrolly and quit it"
    )
    args = parser.parse_args(argv)

    existing = instance.running_port()
    if existing is not None:
        if not args.no_browser:
            webbrowser.open(f"http://127.0.0.1:{existing}")
        return

    port = instance.pick_port(args.port)
    url = f"http://127.0.0.1:{port}"
    app = build_app()
    instance.remember(port)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    try:
        # The window serves until it closes; without one (no display), serve here.
        if (
            args.window
            and window.available()
            and window.run(server, url, open_browser=not args.no_browser)
        ):
            return
        if not args.no_browser:
            threading.Timer(1.0, webbrowser.open, [url]).start()
        server.run()
    finally:
        instance.forget()
