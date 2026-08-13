"""Standalone detailed portfolio view — the full per-position table.
Run directly: python -m launcher.portfolio.cli
"""
from __future__ import annotations

from rich.console import Console

from .data import fetch_positions, load_holdings
from .view import display_portfolio


def main() -> None:
    console = Console()
    try:
        console.print("[dim]Loading holdings...[/dim]")
        holdings = load_holdings()
        console.print(f"[dim]Fetching prices for {len(holdings)} ticker(s)... "
                       "(can take a while over a corporate network/proxy)[/dim]")
        positions = fetch_positions(holdings)
        display_portfolio(positions)
    except Exception as error:
        console.print(f"[red]Error:[/] {error}")

    input("\nPress Enter to close...")


if __name__ == "__main__":
    main()