"""The small window of the Scrolly executable: it says Scrolly is running, opens it, and quits it.

People who start Scrolly with a double-click have no terminal to close, so this window is how they
stop it. The server runs on a thread beside it; closing the window stops the server.
"""

import sys
import threading
import webbrowser
from importlib.util import find_spec
from pathlib import Path

import uvicorn

WAKING = "Scrolly is waking…"
RUNNING = "Scrolly is running in your browser."
FAILED = "Scrolly could not start. See scrolly.log in your .scrolly folder."
CLOSING = "Closing this window stops Scrolly."
POLL_MS = 100


def available() -> bool:
    """Whether this Python can draw the window (some Linux installs lack Tk)."""
    return find_spec("tkinter") is not None


def run(server: uvicorn.Server, url: str, *, open_browser: bool) -> bool:
    """Serve on a thread and show the window until it is closed or Quit is pressed.

    False, with nothing started, when no window can be drawn (no display): serve without it.
    """
    import tkinter as tk
    from tkinter import ttk

    try:
        root = tk.Tk()
    except tk.TclError:
        return False
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    root.title("Scrolly")
    # Inside the executable the icon lies beside the bundled files.
    icon = Path(getattr(sys, "_MEIPASS", "")) / "scrolly-icon.png"
    if hasattr(sys, "_MEIPASS") and icon.exists():
        root.iconphoto(True, tk.PhotoImage(file=str(icon)))
    root.resizable(False, False)
    status = tk.StringVar(value=WAKING)
    ttk.Label(root, textvariable=status).pack(padx=24, pady=(20, 10))
    buttons = ttk.Frame(root)
    buttons.pack(padx=24)
    open_button = ttk.Button(buttons, text="Open Scrolly", command=lambda: webbrowser.open(url))
    open_button.state(["disabled"])
    open_button.pack(side="left", padx=4)

    def quit_scrolly() -> None:
        server.should_exit = True
        root.destroy()

    ttk.Button(buttons, text="Quit", command=quit_scrolly).pack(side="left", padx=4)
    ttk.Label(root, text=CLOSING).pack(padx=24, pady=(10, 20))
    root.protocol("WM_DELETE_WINDOW", quit_scrolly)

    def wait_for_server() -> None:
        if server.started:
            status.set(RUNNING)
            open_button.state(["!disabled"])
            if open_browser:
                webbrowser.open(url)
        elif not thread.is_alive():
            status.set(FAILED)
        else:
            root.after(POLL_MS, wait_for_server)

    root.after(POLL_MS, wait_for_server)
    root.mainloop()
    server.should_exit = True
    thread.join(timeout=5)
    return True
