"""Console rendering for the portfolio. Only this module touches `rich`."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .data import PortfolioPosition, totals_by_currency


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

    for position in positions:
        currency = position.currency
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

    summary_lines = [
        f"{currency}: Value {totals.market_value:,.2f} | "
        f"Gain/Loss {totals.gain_loss:+,.2f} | {totals.gain_loss_pct:+.2f}%"
        for currency, totals in totals_by_currency(positions).items()
    ]

    console.print()
    console.print(Panel("\n".join(summary_lines), title="Portfolio Summary", border_style="blue"))
    console.print()
    console.print("[dim]Data source: Yahoo Finance via yfinance. For personal tracking only.[/dim]")