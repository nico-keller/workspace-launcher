"""BriefingData -> HTML. Pure function, easy to test standalone."""
from __future__ import annotations

from string import Template

from launcher.portfolio.data import CurrencyTotals, PortfolioPosition, totals_by_currency

from .models import BriefingData

_TEMPLATE = Template("""
<html>
<head><meta charset="utf-8">
<style>
  body { background: #1e1e2e; color: #e0e0e0; font-family: 'Segoe UI', sans-serif;
         padding: 28px; margin: 0; }
  h1 { font-size: 20px; font-weight: 600; margin: 0 0 20px; }
  h2 { font-size: 12px; text-transform: uppercase; letter-spacing: 1px;
       color: #8888a0; margin: 18px 0 6px; }
  .value { font-size: 15px; }
  .up { color: #4ade80; } .down { color: #f87171; }
  .event { display: flex; gap: 10px; font-size: 14px; padding: 2px 0; }
  .event time { color: #8888a0; width: 46px; }
  table.portfolio { width: 100%; border-collapse: collapse; font-size: 13px; }
  table.portfolio th { text-align: right; color: #8888a0; font-weight: 500;
                        font-size: 11px; text-transform: uppercase; padding: 4px 6px; }
  table.portfolio th:first-child { text-align: left; }
  table.portfolio td { text-align: right; padding: 4px 6px; border-top: 1px solid #33334a; }
  table.portfolio td:first-child { text-align: left; font-weight: 600; }
  .portfolio-totals { margin-top: 10px; font-size: 13px; color: #c0c0d0; }
  hr { border: none; border-top: 1px solid #33334a; margin: 18px 0; }
  .close-btn { position: absolute; top: 10px; right: 14px; color: #8888a0;
               font-size: 18px; cursor: pointer; line-height: 1; }
  .close-btn:hover { color: #e0e0e0; }
</style>
</head>
<body>
  <div class="close-btn" onclick="pywebview.api.close()">&times;</div>
  <h1>Good morning $greeting_name 👋</h1>
  <hr>
  $portfolio_block
  $weather_block
  $events_block
</body>
</html>
""")


def render(data: BriefingData) -> str:
    return _TEMPLATE.substitute(
        greeting_name=data.greeting_name,
        portfolio_block=_portfolio_block(data),
        weather_block=_weather_block(data),
        events_block=_events_block(data),
    )


def _portfolio_block(data: BriefingData) -> str:
    if not data.positions:
        return ""

    rows = "".join(_position_row(position) for position in data.positions)
    totals_lines = "".join(
        _currency_totals_line(currency, totals)
        for currency, totals in totals_by_currency(data.positions).items()
    )

    return (
        "<h2>Portfolio</h2>"
        '<table class="portfolio"><thead><tr>'
        "<th>Ticker</th><th>Price</th><th>Daily %</th><th>Value</th><th>Gain/Loss %</th>"
        f"</tr></thead><tbody>{rows}</tbody></table>"
        f'<div class="portfolio-totals">{totals_lines}</div>'
    )


def _position_row(position: PortfolioPosition) -> str:
    daily_class = "up" if position.daily_change_pct >= 0 else "down"
    gain_class = "up" if position.unrealized_gain_loss_pct >= 0 else "down"
    return (
        "<tr>"
        f"<td>{position.ticker}</td>"
        f"<td>{position.currency} {position.current_price:,.2f}</td>"
        f'<td class="{daily_class}">{position.daily_change_pct:+.2f}%</td>'
        f"<td>{position.currency} {position.market_value:,.2f}</td>"
        f'<td class="{gain_class}">{position.unrealized_gain_loss_pct:+.2f}%</td>'
        "</tr>"
    )


def _currency_totals_line(currency: str, totals: CurrencyTotals) -> str:
    gain_class = "up" if totals.gain_loss >= 0 else "down"
    return (
        f'<div>{currency} total: {totals.market_value:,.2f} '
        f'(<span class="{gain_class}">{totals.gain_loss:+,.2f} / {totals.gain_loss_pct:+.2f}%</span>)</div>'
    )


def _weather_block(data: BriefingData) -> str:
    if data.weather is None:
        return ""
    w = data.weather
    return f'<h2>Weather {w.location}</h2><div class="value">{w.temperature_c:.0f}°C</div>'


def _events_block(data: BriefingData) -> str:
    if not data.events:
        return ""
    rows = "".join(
        f'<div class="event"><time>{e.start:%H:%M}</time><span>{e.title}</span></div>'
        for e in data.events
    )
    return f"<h2>Today's meetings</h2>{rows}"