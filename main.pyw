from config import GREETING_NAME, TEAMS_URL, WEATHER_LATITUDE, WEATHER_LOCATION, WEATHER_LONGITUDE, WORK_TABS
from launcher.tasks import MorningBriefingTask, OpenTabsTask, OpenTeamsTask

TASKS = [
    OpenTeamsTask(TEAMS_URL),
    OpenTabsTask(WORK_TABS),
    MorningBriefingTask(
        greeting_name=GREETING_NAME,
        weather_location=WEATHER_LOCATION,
        weather_lat=WEATHER_LATITUDE,
        weather_lon=WEATHER_LONGITUDE,
    ),
]


def main() -> None:
    for task in TASKS:
        task.run()


if __name__ == "__main__":
    main()