"""
PyScope — Desktop Launcher
============================
Launches the Streamlit app and opens it in the default browser.
Double-click the .exe (or run this script) to start PyScope.
"""

import os
import sys
import time
import socket
import subprocess
import webbrowser
import threading


def _find_free_port(start: int = 8501, end: int = 8599) -> int:
    """Find an available port in the given range."""
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return 8501


def _wait_for_server(port: int, timeout: int = 30):
    """Block until the Streamlit server is accepting connections."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                return True
        except (ConnectionRefusedError, OSError):
            time.sleep(0.3)
    return False


def main():
    # Determine project directory
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    app_path = os.path.join(base_dir, "app.py")
    port = _find_free_port()
    url = f"http://localhost:{port}"

    print("=" * 50)
    print("  ⬡  PyScope — Code Execution & Profiling Tool")
    print("=" * 50)
    print(f"  Starting server on {url} ...")
    print("  Close this window to stop PyScope.")
    print("=" * 50)

    # Launch Streamlit as a subprocess
    cmd = [
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", str(port),
        "--server.headless", "true",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false",
        "--theme.base", "dark",
    ]

    env = os.environ.copy()
    proc = subprocess.Popen(
        cmd, env=env,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

    # Wait for server to be ready, then open browser
    def _open_browser():
        if _wait_for_server(port):
            print(f"\n  ✓ PyScope is running at {url}")
            print("  Opening browser...\n")
            webbrowser.open(url)
        else:
            print("\n  ✗ Server failed to start. Check the console for errors.")

    threading.Thread(target=_open_browser, daemon=True).start()

    # Keep running until user closes the terminal / presses Ctrl+C
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n  Shutting down PyScope...")
        proc.terminate()
        proc.wait(timeout=5)
        print("  Done.")


if __name__ == "__main__":
    main()
