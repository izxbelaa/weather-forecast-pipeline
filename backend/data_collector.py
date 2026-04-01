from backend.api_client import fetch_weather
from backend.parser import parse_weather
from backend.cleaner import clean_data
from backend.config import CITIES

from database.db import init_db, insert_weather_data
import pandas as pd


def run():

    init_db()

    all_dataframes = []

    for location in CITIES:
        city = location["city"]
        latitude = location["latitude"]
        longitude = location["longitude"]

        data = fetch_weather(latitude, longitude)
        df = parse_weather(data, city, latitude, longitude)
        df = clean_data(df)
        all_dataframes.append(df)

    final_df = pd.concat(all_dataframes, ignore_index=True)

    insert_weather_data(final_df)

    print("Weather data stored successfully")


if __name__ == "__main__":
    run()