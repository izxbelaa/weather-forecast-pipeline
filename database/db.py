import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "weather.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()

    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()


def insert_weather_data(df: pd.DataFrame):

    conn = get_connection()

    query = """
    INSERT OR IGNORE INTO weather_data (
        city,
        timestamp,
        latitude,
        longitude,
        temperature_2m,
        relative_humidity_2m,
        precipitation,
        wind_speed_10m,
        pressure_msl,
        cloud_cover
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    rows = df[
        [
            "city",
            "timestamp",
            "latitude",
            "longitude",
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "pressure_msl",
            "cloud_cover",
        ]
    ].values.tolist()

    conn.executemany(query, rows)

    conn.commit()
    conn.close()