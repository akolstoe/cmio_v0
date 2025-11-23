"""Convenience launcher for the CMIO demo app.

Running ``python run_cmio.py`` from the repository root starts the Flask
application, binding to 0.0.0.0:8000 and opening the dashboard in your default
browser. The script also normalizes the working directory so templates and
static assets resolve correctly even if you invoke it from elsewhere.
"""
from __future__ import annotations

import os
import threading
import webbrowser
from pathlib import Path

from app import app


def _open_browser(port: int) -> None:
    """Open the dashboard in the default browser once the server starts."""
    url = f"http://127.0.0.1:{port}"
    webbrowser.open(url)


def main(port: int = 8000) -> None:
    base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)

    threading.Timer(1.0, _open_browser, args=(port,)).start()
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
