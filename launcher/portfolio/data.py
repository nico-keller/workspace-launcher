"""Portfolio data: loading holdings, fetching live prices, aggregating totals.

Pure data — no console/display coupling — so both the CLI view
(launcher/portfolio/view.py) and the briefing provider
(launcher/providers/portfolio_yfinance.py) can reuse it independently.
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
class PortfolioSummary:
    total_value: float
    currency: str
    change_pct_today: float


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


def _fx_rate(from_currency: str, to_currency: str) -> float:
    if from_currency == to_currency:
        return 1.0
    pair = yf.Ticker(f"{from_currency}{to_currency}=X")
    history = pair.history(period="1d")
    if history.empty:
        raise ValueError(f"No FX rate available for {from_currency}->{to_currency}")
    return float(history["Close"].iloc[-1])


def summarize(positions: list[PortfolioPosition], target_currency: str = "CHF") -> PortfolioSummary:
    """Aggregate possibly-mixed-currency positions into one total via live FX rates."""
    total_today = 0.0
    total_yesterday = 0.0
    fx_cache: dict[str, float] = {}

    for position in positions:
        if position.currency not in fx_cache:
            fx_cache[position.currency] = _fx_rate(position.currency, target_currency)
        rate = fx_cache[position.currency]

        total_today += position.market_value * rate
        total_yesterday += position.shares * position.previous_close * rate

    change_pct = ((total_today - total_yesterday) / total_yesterday * 100) if total_yesterday else 0.0
    return PortfolioSummary(total_value=total_today, currency=target_currency, change_pct_today=change_pct)