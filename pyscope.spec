# -*- mode: python ; coding: utf-8 -*-
"""
PyScope -- PyInstaller Spec File
================================
Builds a standalone .exe that launches the Streamlit app.
"""

import os
import sys
import importlib

from PyInstaller.utils.hooks import copy_metadata, collect_all

# ── Locate key packages ──────────────────────────────────────────────────────
def _pkg_path(name):
    mod = importlib.import_module(name)
    return os.path.dirname(mod.__file__)

streamlit_dir = _pkg_path("streamlit")
altair_dir    = _pkg_path("altair")
plotly_dir    = _pkg_path("plotly")

# ── Collect dist-info metadata for packages that check their own version ─────
metadata_datas = []
_metadata_packages = [
    "streamlit", "altair", "plotly", "matplotlib", "numpy", "psutil",
    "Pillow", "pyarrow", "pandas", "toml", "gitdb", "watchdog", "click",
    "packaging", "tornado", "protobuf", "pydeck", "cachetools",
    "typing-extensions", "rich", "markdown-it-py", "mdurl", "pygments",
    "jinja2", "jsonschema", "attrs", "referencing", "rpds-py",
    "jsonschema-specifications", "narwhals", "tenacity", "blinker",
]
for _pkg in _metadata_packages:
    try:
        metadata_datas += copy_metadata(_pkg)
    except Exception:
        pass   # Skip packages not installed

# ── Project source files to bundle ───────────────────────────────────────────
PROJECT_DIR = os.path.abspath(".")

project_data = [
    (os.path.join(PROJECT_DIR, "app.py"), "."),
    (os.path.join(PROJECT_DIR, "execution_engine.py"), "."),
    (os.path.join(PROJECT_DIR, "execution_monitor.py"), "."),
    (os.path.join(PROJECT_DIR, "multi_lang_runner.py"), "."),
    (os.path.join(PROJECT_DIR, "insights.py"), "."),
    (os.path.join(PROJECT_DIR, "graph_utils.py"), "."),
    (os.path.join(PROJECT_DIR, "ui_components.py"), "."),
    (os.path.join(PROJECT_DIR, "ui_styles.py"), "."),
    (os.path.join(PROJECT_DIR, "main_25.py"), "."),
    (os.path.join(PROJECT_DIR, "main_50.py"), "."),
    (os.path.join(PROJECT_DIR, "main_75.py"), "."),
    (os.path.join(PROJECT_DIR, "main_100.py"), "."),
    (os.path.join(PROJECT_DIR, ".streamlit"), ".streamlit"),
]

# ── Collect streamlit static assets (HTML templates, JS, etc.) ───────────────
st_datas, st_binaries, st_hiddenimports = collect_all("streamlit")

# ── Analysis ─────────────────────────────────────────────────────────────────
a = Analysis(
    ["launcher.py"],
    pathex=[PROJECT_DIR],
    binaries=st_binaries,
    datas=[
        (streamlit_dir, "streamlit"),
        (altair_dir, "altair"),
        (plotly_dir, "plotly"),
    ] + project_data + metadata_datas + st_datas,
    hiddenimports=[
        "streamlit",
        "streamlit.runtime",
        "streamlit.runtime.caching",
        "streamlit.runtime.scriptrunner",
        "streamlit.runtime.scriptrunner.script_runner",
        "streamlit.web",
        "streamlit.web.bootstrap",
        "streamlit.web.server",
        "streamlit.web.server.server",
        "streamlit.web.cli",
        "streamlit.commands",
        "streamlit.commands.page_config",
        "streamlit.delta_generator",
        "streamlit.elements",
        "streamlit.config",
        "altair",
        "plotly",
        "plotly.express",
        "plotly.graph_objects",
        "matplotlib",
        "matplotlib.pyplot",
        "matplotlib.backends.backend_agg",
        "numpy",
        "psutil",
        "GPUtil",
        "PIL",
        "PIL.Image",
        "pyarrow",
        "pandas",
        "toml",
        "validators",
        "gitdb",
        "watchdog",
        "click",
        "rich",
        "packaging",
        "importlib_metadata",
        "tornado",
        "tornado.web",
        "tornado.websocket",
        "tornado.ioloop",
        "pydeck",
        "cachetools",
    ] + st_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PyScope",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,       # Keep console to show "server starting..." messages
    icon=None,           # Add an .ico file path here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PyScope",
)
