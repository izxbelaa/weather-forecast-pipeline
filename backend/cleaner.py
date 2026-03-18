import pandas as pd
from datetime import datetime


def clean_data(df):

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df = df.dropna(subset=["timestamp"])
    now = datetime.now()
    df = df[df["timestamp"] <= now]
    df = df.dropna()

    df = df.drop_duplicates()
    df = df.sort_values("timestamp")

    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    return df