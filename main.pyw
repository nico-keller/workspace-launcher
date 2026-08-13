from config import GREETING_NAME, TEAMS_URL, WEATHER_LATITUDE, WEATHER_LOCATION, WEATHER_LONGITUDE, WORK_TABS
from launcher.tasks import MorningBriefingTask, OpenTabsTask, OpenTeamsTask, OpenPortfolioDashboardTask

# TASKS is built here, not in config.py — config.py stays a plain-settings
# leaf module with no imports from `launcher`, which avoids the circular
# import you hit (launcher.portfolio.data needs config.PORTFOLIO_FILE;
# config importing launcher.tasks would loop straight back).
TASKS = [
    OpenTeamsTask(TEAMS_URL),
    OpenTabsTask(WORK_TABS),
    MorningBriefingTask(
        greeting_name=GREETING_NAME,
        weather_location=WEATHER_LOCATION,
        weather_lat=WEATHER_LATITUDE,
        weather_lon=WEATHER_LONGITUDE,
    )
    # Swap in for the full per-position table instead of the summary:
    #OpenPortfolioDashboardTask()
]


def main() -> None:
    for task in TASKS:
        task.run()


if __name__ == "__main__":
    main()