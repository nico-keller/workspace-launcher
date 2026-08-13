"""Abstractions BriefingService depends on — not concrete providers."""
from __future__ import annotations

from typing import Protocol

from launcher.portfolio.data import PortfolioSummary

from .models import CalendarEvent, WeatherSnapshot


class PortfolioProvider(Protocol):
    def get_summary(self) -> PortfolioSummary: ...


class WeatherProvider(Protocol):
    def get_snapshot(self) -> WeatherSnapshot: ...


class CalendarProvider(Protocol):
    def get_todays_events(self) -> list[CalendarEvent]: ...