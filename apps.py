"""Launchers for the morning routine: Teams and the portfolio dashboard."""

import subprocess
from pathlib import Path
import os

from config import TEAMS_URL


def open_teams() -> None:
    os.system(TEAMS_URL)


def open_portfolio_dashboard() -> None:
    """Launch the portfolio script in a new PowerShell window."""
    portfolio_script = Path(__file__).with_name("portfolio.py")

    if not portfolio_script.exists():
        raise FileNotFoundError(f"Portfolio script not found: {portfolio_script}")

    subprocess.Popen(
        [
            "powershell",
            "-NoExit",
            "-Command",
            f'py "{portfolio_script}"',
        ]
    )