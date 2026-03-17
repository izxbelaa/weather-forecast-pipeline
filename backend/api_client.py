import requests
from backend.config import LATITUDE, LONGITUDE, HOURLY_VARS, API_URL, START_DATE, END_DATE


def fetch_weather():

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": ",".join(HOURLY_VARS),
        "timezone": "auto"
    }

    response = requests.get(API_URL, params=params)

    return response.json()