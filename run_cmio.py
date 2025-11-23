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


def _ensure_dependencies() -> None:
    """Validate Flask is available and provide clear install guidance."""

    try:
        import flask  # noqa: F401
    except ModuleNotFoundError:
        message = (
            "CMIO requires Flask. Install dependencies first with:\n"
            "  python -m pip install -r requirements.txt\n"
            "Then re-run: python run_cmio.py"
        )
        print(message)
        raise SystemExit(1)


def _open_browser(port: int) -> None:
    """Open the dashboard in the default browser once the server starts."""
    url = f"http://127.0.0.1:{port}"
    webbrowser.open(url)


def main(port: int = 8000) -> None:
    base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)

    _ensure_dependencies()

    from app import app

    threading.Timer(1.0, _open_browser, args=(port,)).start()
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
