import json
from dataclasses import dataclass
from pathlib import Path

import yfinance as yf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

PORTFOLIO_FILE = Path(__file__).with_name("portfolio.local.json")

@dataclass
class Holding:
    ticker: str
    shares: float
    avg_cost: float
    currency: str


@dataclass
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


def get_position(holding: Holding) -> PortfolioPosition:
    ticker = yf.Ticker(holding.ticker)
    history = ticker.history(period="5d")

    if history.empty:
        raise ValueError(f"No price data found for ticker: {holding.ticker}")

    current_price = float(history["Close"].iloc[-1])

    if len(history) >= 2:
        previous_close = float(history["Close"].iloc[-2])
    else:
        previous_close = current_price

    return PortfolioPosition(
        ticker=holding.ticker,
        shares=holding.shares,
        avg_cost=holding.avg_cost,
        currency=holding.currency,
        current_price=current_price,
        previous_close=previous_close,
    )


def format_money(value: float, currency: str) -> str:
    return f"{currency} {value:,.2f}"


def format_percent(value: float) -> str:
    return f"{value:+.2f}%"


def gain_loss_style(value: float) -> str:
    if value > 0:
        return "green"
    if value < 0:
        return "red"
    return "white"


def display_portfolio(positions: list[PortfolioPosition]) -> None:
    console = Console()

    table = Table(title="Portfolio Performance")

    table.add_column("Ticker", style="bold")
    table.add_column("Shares", justify="right")
    table.add_column("Avg Cost", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Daily %", justify="right")
    table.add_column("Market Value", justify="right")
    table.add_column("Gain/Loss", justify="right")
    table.add_column("Gain/Loss %", justify="right")

    totals_by_currency: dict[str, dict[str, float]] = {}

    for position in positions:
        currency = position.currency

        totals_by_currency.setdefault(
            currency,
            {"market_value": 0.0, "cost_basis": 0.0, "gain_loss": 0.0},
        )

        totals_by_currency[currency]["market_value"] += position.market_value
        totals_by_currency[currency]["cost_basis"] += position.cost_basis
        totals_by_currency[currency]["gain_loss"] += position.unrealized_gain_loss

        table.add_row(
            position.ticker,
            f"{position.shares:,.4f}",
            format_money(position.avg_cost, currency),
            format_money(position.current_price, currency),
            f"[{gain_loss_style(position.daily_change_pct)}]{format_percent(position.daily_change_pct)}[/]",
            format_money(position.market_value, currency),
            f"[{gain_loss_style(position.unrealized_gain_loss)}]{format_money(position.unrealized_gain_loss, currency)}[/]",
            f"[{gain_loss_style(position.unrealized_gain_loss_pct)}]{format_percent(position.unrealized_gain_loss_pct)}[/]",
        )

    console.print()
    console.print(table)

    summary_lines = []

    for currency, totals in totals_by_currency.items():
        total_gain_pct = (
            totals["gain_loss"] / totals["cost_basis"] * 100
            if totals["cost_basis"]
            else 0
        )

        summary_lines.append(
            f"{currency}: "
            f"Value {totals['market_value']:,.2f} | "
            f"Gain/Loss {totals['gain_loss']:+,.2f} | "
            f"{total_gain_pct:+.2f}%"
        )

    console.print()
    console.print(
        Panel(
            "\n".join(summary_lines),
            title="Portfolio Summary",
            border_style="blue",
        )
    )

    console.print()
    console.print("[dim]Data source: Yahoo Finance via yfinance. For personal tracking only.[/dim]")


def main() -> None:
    console = Console()

    try:
        holdings = load_holdings()
        positions = [get_position(holding) for holding in holdings]
        display_portfolio(positions)
    except Exception as error:
        console.print(f"[red]Error:[/] {error}")

    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()