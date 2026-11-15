import json
import urllib.request


WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast?latitude=38.72&longitude=-9.14"
    "&daily=precipitation_sum,temperature_2m_max&timezone=Europe/Lisbon&forecast_days=1"
)


def fetch_lisbon_weather():
    with urllib.request.urlopen(WEATHER_URL, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))
