from datetime import datetime, timedelta

CITIES = [
    {"city": "Limassol", "latitude": 34.6786, "longitude": 33.0413},
    {"city": "Nicosia", "latitude": 35.1856, "longitude": 33.3823},
    {"city": "Larnaca", "latitude": 34.9192, "longitude": 33.6232},
    {"city": "Paphos", "latitude": 34.7721, "longitude": 32.4297},
]

today = datetime.today()

START_DATE = (today - timedelta(days=90)).strftime("%Y-%m-%d")
END_DATE = today.strftime("%Y-%m-%d")

HOURLY_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "pressure_msl",
    "cloud_cover"
]

API_URL = "https://archive-api.open-meteo.com/v1/archive"