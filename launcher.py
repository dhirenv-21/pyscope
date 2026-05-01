"""
PyScope -- Desktop Launcher
============================
Launches the Streamlit app directly (works both as .py and as frozen .exe).
Double-click the .exe (or run this script) to start PyScope.
"""

import os
import sys
import io
import time
import threading
import webbrowser


def main():
    # ── Force UTF-8 output so Unicode chars survive on Windows consoles ──
    if sys.stdout is None or (hasattr(sys.stdout, "encoding") and sys.stdout.encoding != "utf-8"):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer if hasattr(sys.stdout, "buffer") else open(os.devnull, "wb"),
                encoding="utf-8", errors="replace", line_buffering=True,
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer if hasattr(sys.stderr, "buffer") else open(os.devnull, "wb"),
                encoding="utf-8", errors="replace", line_buffering=True,
            )
        except Exception:
            pass  # Absolute worst case: leave stdout as-is

    # ── Determine base directory ──────────────────────────────────────────
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    app_path = os.path.join(base_dir, "app.py")
    port = "8501"
    url = f"http://localhost:{port}"

    print("=" * 50)
    print("  PyScope -- Code Execution & Profiling Tool")
    print("=" * 50)
    print(f"  Starting server on {url} ...")
    print("  Close this window to stop PyScope.")
    print("=" * 50)

    # ── Auto-open browser after a short delay ─────────────────────────────
    def _open_browser():
        time.sleep(4)
        print(f"\n  -> Opening browser at {url}")
        webbrowser.open(url)

    threading.Thread(target=_open_browser, daemon=True).start()

    # ── Boot Streamlit directly in this process ───────────────────────────
    # Force production mode — PyInstaller bundles streamlit source which
    # causes it to incorrectly detect developmentMode=true.
    os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    sys.argv = [
        "streamlit", "run", app_path,
        "--global.developmentMode", "false",
        "--server.port", port,
        "--server.headless", "true",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false",
        "--browser.serverAddress", "localhost",
        "--theme.base", "dark",
    ]

    from streamlit.web import cli as stcli
    stcli.main()


if __name__ == "__main__":
    main()
