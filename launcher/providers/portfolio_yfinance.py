"""Portfolio provider for the briefing — thin wrapper around launcher.portfolio.data."""
from __future__ import annotations

from launcher.portfolio.data import PortfolioSummary, fetch_positions, load_holdings, summarize


class YFinancePortfolioProvider:
    def __init__(self, target_currency: str = "CHF") -> None:
        self._target_currency = target_currency

    def get_summary(self) -> PortfolioSummary:
        holdings = load_holdings()
        positions = fetch_positions(holdings)
        return summarize(positions, target_currency=self._target_currency)