"""Portfolio provider for the briefing — thin wrapper around launcher.portfolio.data."""
from __future__ import annotations

from launcher.portfolio.data import PortfolioPosition, fetch_positions, load_holdings


class YFinancePortfolioProvider:
    """Full per-position detail, in each position's native currency —
    the briefing window renders the same table the old standalone
    dashboard did.
    """

    def get_positions(self) -> list[PortfolioPosition]:
        holdings = load_holdings()
        return fetch_positions(holdings)