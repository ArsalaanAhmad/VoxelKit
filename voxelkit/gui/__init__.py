"""Optional local GUI launcher for VoxelKit."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path


GUI_MISSING_DEPENDENCY_MESSAGE = "Install GUI extras with: pip install voxelkit[gui]"


def run_gui() -> int:
    """Launch the local Streamlit GUI application.

    Returns:
        Exit code from the Streamlit process.

    Raises:
        ModuleNotFoundError: If Streamlit is not installed.
    """
    if importlib.util.find_spec("streamlit") is None:
        raise ModuleNotFoundError(GUI_MISSING_DEPENDENCY_MESSAGE)

    app_path = Path(__file__).with_name("app.py")
    env = os.environ.copy()
    # Keep usage fully local and disable usage stats for this prototype.
    env.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--browser.gatherUsageStats=false",
    ]
    return subprocess.call(command, env=env)


__all__ = ["GUI_MISSING_DEPENDENCY_MESSAGE", "run_gui"]
