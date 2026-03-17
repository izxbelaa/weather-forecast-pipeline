from backend.api_client import fetch_weather
from backend.parser import parse_weather
from backend.cleaner import clean_data

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.db import init_db, insert_weather_data


def run():

    init_db()

    data = fetch_weather()

    df = parse_weather(data)

    df = clean_data(df)

    insert_weather_data(df)

    print("Weather data stored successfully")


if __name__ == "__main__":
    run()