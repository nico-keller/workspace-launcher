"""Immutable data models for the Morning Briefing window."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time

from launcher.portfolio.data import PortfolioPosition


@dataclass(frozen=True, slots=True)
class WeatherSnapshot:
    location: str
    temperature_c: float


@dataclass(frozen=True, slots=True)
class CalendarEvent:
    title: str
    start: time


@dataclass(frozen=True, slots=True)
class BriefingData:
    greeting_name: str
    positions: tuple[PortfolioPosition, ...]
    weather: WeatherSnapshot | None
    events: tuple[CalendarEvent, ...] = field(default_factory=tuple)