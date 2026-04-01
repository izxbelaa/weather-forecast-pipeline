import requests
from backend.config import HOURLY_VARS, API_URL, START_DATE, END_DATE


def fetch_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": ",".join(HOURLY_VARS),
        "timezone": "auto"
    }

    response = requests.get(API_URL, params=params)

    return response.json()