"""Portfolio data: loading holdings, fetching live prices, aggregating totals.

Pure data — no console/display coupling — so both the CLI view
(launcher/portfolio/view.py) and the briefing renderer
(launcher/briefing/renderer.py) can reuse it independently.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

import yfinance as yf

from config import PORTFOLIO_FILE


@dataclass(frozen=True, slots=True)
class Holding:
    ticker: str
    shares: float
    avg_cost: float
    currency: str


@dataclass(frozen=True, slots=True)
class PortfolioPosition:
    ticker: str
    shares: float
    avg_cost: float
    currency: str
    current_price: float
    previous_close: float

    @property
    def market_value(self) -> float:
        return self.shares * self.current_price

    @property
    def cost_basis(self) -> float:
        return self.shares * self.avg_cost

    @property
    def unrealized_gain_loss(self) -> float:
        return self.market_value - self.cost_basis

    @property
    def unrealized_gain_loss_pct(self) -> float:
        if self.cost_basis == 0:
            return 0
        return self.unrealized_gain_loss / self.cost_basis * 100

    @property
    def daily_change(self) -> float:
        return self.current_price - self.previous_close

    @property
    def daily_change_pct(self) -> float:
        if self.previous_close == 0:
            return 0
        return self.daily_change / self.previous_close * 100


@dataclass(frozen=True, slots=True)
class CurrencyTotals:
    market_value: float
    cost_basis: float
    gain_loss: float

    @property
    def gain_loss_pct(self) -> float:
        return self.gain_loss / self.cost_basis * 100 if self.cost_basis else 0.0


def load_holdings() -> list[Holding]:
    if not PORTFOLIO_FILE.exists():
        raise FileNotFoundError(
            f"Portfolio file not found: {PORTFOLIO_FILE}\n"
            "Create a portfolio.local.json file based on portfolio.sample.json."
        )

    with open(PORTFOLIO_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return [
        Holding(
            ticker=item["ticker"],
            shares=float(item["shares"]),
            avg_cost=float(item["avg_cost"]),
            currency=item.get("currency", "USD"),
        )
        for item in data["holdings"]
    ]


def fetch_positions(holdings: list[Holding]) -> list[PortfolioPosition]:
    """Fetch prices for all holdings in one batched call instead of one per ticker."""
    if not holdings:
        return []

    tickers = [holding.ticker for holding in holdings]
    history = yf.download(
        tickers=tickers, period="5d", group_by="ticker", threads=True, progress=False,
    )

    positions = []
    for holding in holdings:
        ticker_history = history[holding.ticker] if len(tickers) > 1 else history
        closes = ticker_history["Close"].dropna()

        if closes.empty:
            raise ValueError(f"No price data found for ticker: {holding.ticker}")

        current_price = float(closes.iloc[-1])
        previous_close = float(closes.iloc[-2]) if len(closes) >= 2 else current_price

        positions.append(
            PortfolioPosition(
                ticker=holding.ticker,
                shares=holding.shares,
                avg_cost=holding.avg_cost,
                currency=holding.currency,
                current_price=current_price,
                previous_close=previous_close,
            )
        )
    return positions


def totals_by_currency(positions: list[PortfolioPosition]) -> dict[str, CurrencyTotals]:
    """Aggregate positions per their native currency — no FX conversion.

    Shared by the CLI table and the briefing HTML table so the two views
    can't drift apart on how they sum things up.
    """
    totals: dict[str, CurrencyTotals] = {}
    for position in positions:
        running = totals.get(position.currency, CurrencyTotals(0.0, 0.0, 0.0))
        totals[position.currency] = CurrencyTotals(
            market_value=running.market_value + position.market_value,
            cost_basis=running.cost_basis + position.cost_basis,
            gain_loss=running.gain_loss + position.unrealized_gain_loss,
        )
    return totals