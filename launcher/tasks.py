"""Each step of the morning routine is a Task. main.py just runs whatever's
in the list — adding a step means adding a Task, not editing control flow.
"""
from __future__ import annotations

import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Protocol

from launcher.briefing.renderer import render
from launcher.briefing.service import BriefingService
from launcher.briefing.window import show
from launcher.providers.calendar_outlook import OutlookCalendarProvider
from launcher.providers.portfolio_yfinance import YFinancePortfolioProvider
from launcher.providers.weather_openmeteo import OpenMeteoWeatherProvider

_REPO_ROOT = Path(__file__).resolve().parent.parent


class Task(Protocol):
    def run(self) -> None: ...


class OpenTeamsTask:
    """Launches the Teams desktop app via its URI handler (not the browser).

    Uses os.system rather than os.startfile because teams_url is itself a
    shell command (e.g. "start msteams:") that needs a shell to interpret
    the `start` verb — os.startfile expects a bare path/URL, not a command.
    """

    def __init__(self, teams_url: str) -> None:
        self._teams_url = teams_url

    def run(self) -> None:
        os.system(self._teams_url)  # noqa: S605 — fixed, non-user-controlled command


class OpenTabsTask:
    """Opens the configured work tabs in the default browser."""

    def __init__(self, urls: list[str]) -> None:
        self._urls = urls

    def run(self) -> None:
        for url in self._urls:
            webbrowser.open_new_tab(url)


class OpenPortfolioDashboardTask:
    """Original detailed table view — kept for on-demand deep dives."""

    def run(self) -> None:
        subprocess.Popen(
            ["powershell", "-NoExit", "-Command", f'& "{sys.executable}" -m launcher.portfolio.cli'],
            cwd=_REPO_ROOT,
        )


class MorningBriefingTask:
    """Summarized portfolio + weather + today's meetings in one window."""

    def __init__(self, greeting_name: str, weather_location: str, weather_lat: float, weather_lon: float) -> None:
        self._service = BriefingService(
            greeting_name=greeting_name,
            portfolio_provider=YFinancePortfolioProvider(),
            weather_provider=OpenMeteoWeatherProvider(weather_location, weather_lat, weather_lon),
            calendar_provider=OutlookCalendarProvider(),
        )

    def run(self) -> None:
        # build() (network calls to yfinance/Outlook/Open-Meteo) runs only
        # after the window is already visible — see briefing/window.py.
        show(lambda: render(self._service.build()))