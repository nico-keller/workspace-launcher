# workspace-launcher

Automates a morning routine on Windows: launches your apps/tabs and shows a
briefing window with portfolio performance, local weather, and today's
calendar — all in one place, one click after login.

Windows-only (relies on Outlook COM automation and native URI launching).

## Structure

```
workspace-launcher/
├── main.py                    # entry point — declares which Tasks run
├── config.py                  # URLs, file paths, personal settings (gitignored)
├── portfolio.sample.json      # template — copy to portfolio.local.json
├── portfolio.local.json       # your real holdings (gitignored)
├── requirements.txt
└── launcher/                  # the package — all the actual logic
    ├── tasks.py                 # Task protocol + OpenTeamsTask, MorningBriefingTask, ...
    ├── browser.py                # opens a list of URLs as browser tabs
    ├── portfolio/
    │   ├── data.py                 # loading holdings, fetching prices, FX-aware totals
    │   ├── view.py                  # rich console table (the detailed view)
    │   └── cli.py                    # `python -m launcher.portfolio.cli` — standalone table
    ├── briefing/
    │   ├── models.py                # BriefingData, WeatherSnapshot, CalendarEvent
    │   ├── interfaces.py            # PortfolioProvider / WeatherProvider / CalendarProvider protocols
    │   ├── service.py               # fetches all three concurrently, degrades gracefully
    │   ├── renderer.py              # BriefingData -> HTML
    │   └── window.py                # shows the HTML in a native pywebview window
    └── providers/
        ├── portfolio_yfinance.py    # implements PortfolioProvider using launcher.portfolio.data
        ├── weather_openmeteo.py     # implements WeatherProvider using Open-Meteo
        └── calendar_outlook.py      # implements CalendarProvider using local Outlook (COM)
```

**Why this shape:** `portfolio/`, `briefing/`, and `providers/` are three
genuinely separate concerns, so they're separate sub-packages rather than
same-level files. `providers/` implements the `Protocol`s declared in
`briefing/interfaces.py` — that's what lets `briefing/service.py` stay
ignorant of yfinance, Outlook, or Open-Meteo specifically. Swapping the
calendar source later means writing a new provider class; nothing in
`briefing/` changes.

## Privacy by design

None of your personal data ever needs to be committed:

- `config.py` and `portfolio.local.json` are both listed in `.gitignore`.
  Everything person-specific (launch URLs, your name, your holdings, your
  city's coordinates) lives only in those two local files.
- The repo ships `portfolio.sample.json` as a template, not real data.
- No credentials, tokens, or API keys are stored anywhere — Outlook access
  goes through local COM automation, prices come from the public Open-Meteo
  and Yahoo Finance APIs, and neither requires a key.

If you fork or share this project, double-check `git status` before pushing
to confirm `config.py` and `portfolio.local.json` are still untracked.

## Setup

```bash
git clone <this repo>
cd workspace-launcher
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

copy portfolio.sample.json portfolio.local.json
# edit portfolio.local.json with your real holdings
```

Create your own `config.py` in the project root (it's gitignored, so it
stays local) with your personal settings, for example:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PORTFOLIO_FILE = BASE_DIR / "portfolio.local.json"

TEAMS_URL = "start msteams:"

WORK_TABS = [
    "https://example.com/inbox",
    "https://example.com/dashboard",
]

GREETING_NAME = "Your Name"
WEATHER_LOCATION = "Your City"
WEATHER_LATITUDE = 0.0
WEATHER_LONGITUDE = 0.0
```

`PORTFOLIO_FILE` should point at `portfolio.local.json`; everything else is
whatever apps, tabs, and personal details you want the launcher to use.

## Running

```bash
python main.py
```

This runs whatever's listed in `TASKS` inside `main.py` — by default,
opens Teams and shows the Morning Briefing window. To see the full
per-position portfolio table instead of (or alongside) the summary,
uncomment `OpenPortfolioDashboardTask()` in `main.py`, or run it directly:

```bash
python -m launcher.portfolio.cli
```

## Adding a new morning-routine step

Add a class with a `run()` method to `launcher/tasks.py`, then append an
instance to `TASKS` in `main.py`. No other file needs to change.

## Adding a new briefing data source

Write a class that implements one of the `Protocol`s in
`launcher/briefing/interfaces.py` (e.g. a `CalendarProvider` backed by
Google Calendar instead of Outlook), drop it in `launcher/providers/`,
and pass it into `BriefingService` in `MorningBriefingTask.__init__`.

## Notes

- `portfolio.local.json` is gitignored — it's your real position sizes,
  never commit it.
- Portfolio totals are converted to a target currency via live FX rates
  (`launcher/portfolio/data.py:summarize`), useful if your holdings are in
  a different currency than your home currency. Worth spot-checking the
  converted total against your broker's own number occasionally.
- If Outlook isn't open, or there's no network for weather/FX, the
  briefing still shows — `BriefingService` fetches all three sources
  concurrently and independently, so one failing just leaves that section
  blank instead of crashing the window.
