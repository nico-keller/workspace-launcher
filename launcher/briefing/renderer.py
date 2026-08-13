"""BriefingData -> HTML. Pure function, easy to test standalone."""
from __future__ import annotations

from string import Template

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
    if data.portfolio is None:
        return ""
    p = data.portfolio
    direction_class = "up" if p.change_pct_today >= 0 else "down"
    sign = "+" if p.change_pct_today >= 0 else ""
    return (
        f'<h2>Portfolio</h2>'
        f'<div class="value {direction_class}">{sign}{p.change_pct_today:.2f}% today</div>'
        f'<div class="value">{p.currency} {p.total_value:,.0f} total value</div>'
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