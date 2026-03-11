from datetime import datetime, timedelta

CITY = "Limassol"

LATITUDE = 34.6786
LONGITUDE = 33.0413

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