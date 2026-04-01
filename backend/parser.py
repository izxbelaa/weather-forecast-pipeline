import pandas as pd


def parse_weather(json_data, city, latitude, longitude):
    hourly = json_data["hourly"]

    df = pd.DataFrame({
        "timestamp": hourly["time"],
        "temperature_2m": hourly["temperature_2m"],
        "relative_humidity_2m": hourly["relative_humidity_2m"],
        "precipitation": hourly["precipitation"],
        "wind_speed_10m": hourly["wind_speed_10m"],
        "pressure_msl": hourly["pressure_msl"],
        "cloud_cover": hourly["cloud_cover"]
    })

    df["city"] = city
    df["latitude"] = latitude
    df["longitude"] = longitude

    return df