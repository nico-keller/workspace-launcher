"""Weather from Open-Meteo. Free, no API key."""
from __future__ import annotations

import requests

from launcher.briefing.models import WeatherSnapshot

_URL = "https://api.open-meteo.com/v1/forecast"


class OpenMeteoWeatherProvider:
    def __init__(self, location_name: str, latitude: float, longitude: float, timeout: float = 5.0) -> None:
        self._location_name = location_name
        self._latitude = latitude
        self._longitude = longitude
        self._timeout = timeout

    def get_snapshot(self) -> WeatherSnapshot:
        response = requests.get(
            _URL,
            params={"latitude": self._latitude, "longitude": self._longitude, "current": "temperature_2m"},
            timeout=self._timeout,
        )
        response.raise_for_status()
        current = response.json()["current"]
        return WeatherSnapshot(location=self._location_name, temperature_c=current["temperature_2m"])