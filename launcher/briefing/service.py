"""Fetches from all providers concurrently; one failing doesn't take down
the whole briefing.
"""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

from .interfaces import CalendarProvider, PortfolioProvider, WeatherProvider
from .models import BriefingData

logger = logging.getLogger(__name__)


class BriefingService:
    def __init__(
        self,
        greeting_name: str,
        portfolio_provider: PortfolioProvider,
        weather_provider: WeatherProvider,
        calendar_provider: CalendarProvider,
    ) -> None:
        self._greeting_name = greeting_name
        self._portfolio_provider = portfolio_provider
        self._weather_provider = weather_provider
        self._calendar_provider = calendar_provider

    def build(self) -> BriefingData:
        with ThreadPoolExecutor(max_workers=3) as executor:
            portfolio_future = executor.submit(
                self._safe_call, self._portfolio_provider.get_positions, default=[]
            )
            weather_future = executor.submit(self._safe_call, self._weather_provider.get_snapshot)
            events_future = executor.submit(self._safe_call, self._calendar_provider.get_todays_events, default=[])

        return BriefingData(
            greeting_name=self._greeting_name,
            positions=tuple(portfolio_future.result()),
            weather=weather_future.result(),
            events=tuple(events_future.result()),
        )

    @staticmethod
    def _safe_call(func, default=None):
        try:
            return func()
        except Exception:
            logger.exception("Briefing provider failed: %s", func.__qualname__)
            return default